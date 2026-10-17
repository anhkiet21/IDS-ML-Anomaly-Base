"""Điểm chạy pipeline RAW → AUDIT → CLEAN → VALIDATE → SPLIT → SAVE."""
import argparse
import json
import logging
import sys
from pathlib import Path
import numpy as np
import pandas as pd
from .config import ROOT, EXCLUDED, IDENTIFIERS
from .reporting import save_json, table
from .load_data import load_all_datasets, validate_schema
from .data_audit import analyze_data_types, analyze_missing_values, analyze_infinity_values, analyze_duplicates
from .clean_data import clean_non_finite_values
from .feature_audit import audit_features, select_train_features
from .split_data import create_dataset_splits, split_statistics
from .validation import validate_dataset_splits, check_cross_split_duplicates, cleanup_split_duplicates

def log_stage(name, before, data):
    """Ghi số hàng và dung lượng tại mỗi bước lớn."""
    logging.info('%s: rows before=%d after=%d memory bytes=%d', name, before, len(data), data.memory_usage(deep=True).sum())

def analyze_labels(data):
    """Đếm nhãn thực tế sau làm sạch."""
    labels = data.Label.value_counts().rename_axis('Label').reset_index(name='Count')
    labels['Percentage'] = labels.Count / len(data) * 100
    days = data.groupby(['source_day','Label'], observed=True).size().reset_index(name='Count')
    days['Percentage'] = days.Count / days.groupby('source_day', observed=True).Count.transform('sum') * 100
    return labels, days

def save_cleaned_dataset(data, path):
    """Lưu Parquet không kèm index; không sửa file raw."""
    data.to_parquet(path, engine='pyarrow', index=False, compression='snappy')

def save_splits(splits, output):
    """Lưu bốn split đã được xác thực."""
    for name,df in splits.items():
        save_cleaned_dataset(df, output / f'{name}.parquet')

def generate_preprocessing_report(reports, overview, schema, conversions, missing, duplicate, quality, cleaning, labels, days, stats, leakage, features):
    """Ghép báo cáo Markdown từ kết quả tính trực tiếp trên dữ liệu."""
    sections = [('# CICIDS2017 preprocessing report', 'PASS: kiểm tra nhãn, ngày, numeric và hữu hạn đã hoàn tất. Không train, scale, chọn threshold hoặc loại outlier.'),
        ('Dataset overview', table(pd.DataFrame([{k:a[k] for k in ['file','physical_rows','comma_only_rows','structured_rows','columns','benign','attack','nan','positive_inf','negative_inf','duplicate','memory_bytes']} for a in overview])) + '\n\nPhysical rows = số record dữ liệu đọc từ CSV, không tính header; comma-only/malformed = mọi raw columns đều NaN, loại ngay sau read_csv trước metadata. Structured rows = physical rows − malformed rows.'),
        ('Schema analysis', '```json\n' + json.dumps(schema, ensure_ascii=False, indent=2) + '\n```\n\nConversion: ' + str(conversions) + '\n\nPandas phân biệt tên header trùng bằng hậu tố .1; ánh xạ được lưu trong dataset_overview.json. Flow ID, Source IP, Destination IP, Timestamp được giữ làm metadata vì là định danh/thời gian; không dùng làm model input.'),
        ('Label distribution', table(labels) + '\n\n' + table(days)),
        ('Missing / Infinity', table(missing.loc[(missing['NaN Count'] + missing['Total Inf']) > 0]) + '\n\n' + str(cleaning['non_finite'])),
        ('Duplicate analysis', table(pd.DataFrame([{'Stage': stage, 'Full duplicates': duplicate[stage]['full_duplicates'], 'Feature + Label duplicates': duplicate[stage]['feature_label_duplicates'], 'Label conflict groups': duplicate[stage]['conflict_groups']} for stage in ['before','after']])) + '\n\n' + table(pd.DataFrame([{'Split': name, 'Rows before': values['rows_before'], 'Within-split duplicates removed': values['within_split_duplicates_removed'], 'Overlap rows removed': values['cross_split_rows_removed'], 'Rows after': values['rows_after']} for name,values in duplicate['cleanup']['splits'].items()])) + '\n\nKhông global-dedup trước split. Trong mỗi split giữ hàng đầu theo model features + Label. Giữ conflict khác Label trong cùng split; overlap giữa split được loại bất kể Label theo ưu tiên Train → Calibration → Selection → Test. Chi tiết số hàng và nhãn bị loại: duplicate_report.json.'),
        ('Feature quality', f"Chỉ khảo sát và quyết định trên Train trước cleanup. Numeric features cuối: {len(features)}. Constant features removed: {quality['selection']['constant_features_removed']}. Duplicate features removed: {quality['selection']['duplicate_features_removed']}. Near-constant: {len(quality['near_constant_features'])}; high correlation pairs: {len(quality['highly_correlated_pairs'])}; chỉ report, không xóa hai nhóm này. Chi tiết: feature_quality_report.json, basic_statistics.csv và correlation_matrix.csv (Train)."),
        ('Cleaning result', f"Physical rows {cleaning['physical_rows']} → loại comma-only {cleaning['comma_only_rows']} → structured rows {cleaning['structured_rows']} → actual NaN/Inf rows loại {cleaning['rows_removed_nan_inf']} → split trước cleanup {cleaning['rows_before_duplicate_cleanup']} → duplicate/overlap rows loại {cleaning['rows_removed_duplicates']} → final rows {cleaning['final_rows']}"),
        ('Dataset splitting', 'Monday BENIGN: 80% đầu Train, 20% cuối Calibration, tính sau NaN/Inf cleaning và trước dedup; không shuffle hoặc re-split sau cleanup. Tuesday/Wednesday/Thursday → Selection. Friday → Test. Số hàng trước cleanup: ' + json.dumps(cleaning['split_statistics_before_cleanup'], ensure_ascii=False)),
        ('Leakage analysis', '### Before cleanup (all raw numeric features)\n\n' + table(pd.DataFrame(leakage['before_all_numeric_features'])) + '\n\n### Before cleanup (final model features)\n\n' + table(pd.DataFrame(leakage['before'])) + '\n\n### After cleanup (final model features)\n\n' + table(pd.DataFrame(leakage['after'])) + '\n\nDuplicate Feature Rows = số vector duy nhất chung; matching_rows và tỷ lệ tính riêng cho mỗi phía. Hash chỉ lọc ứng viên; mọi overlap được xác nhận bằng so sánh đủ model features, không gồm Label/metadata.'),
        ('Final dataset', table(pd.DataFrame([{'Split': k, 'Rows': v['total'], 'BENIGN': v['benign'], 'ATTACK': v['attack']} for k,v in stats.items()])))]
    (reports / 'preprocessing_report.md').write_text('\n\n'.join(title + '\n\n' + content if title.startswith('#') else '## ' + title + '\n\n' + content for title,content in sections), encoding='utf-8')

def run(raw_dir, output_dir, reports, max_fraction):
    """Chạy các bước theo thứ tự và lưu chứng cứ trước thao tác xóa."""
    reports.mkdir(parents=True, exist_ok=True)
    (output_dir / 'cleaned').mkdir(parents=True, exist_ok=True)
    (output_dir / 'splits').mkdir(parents=True, exist_ok=True)
    frames, overview = load_all_datasets(raw_dir)
    save_json(reports / 'dataset_overview.json', overview)
    schema = validate_schema(frames, overview)
    save_json(reports / 'schema_report.json', schema)
    if not schema['consistent_names']:
        raise ValueError('Schema khác tên cột; xem schema_report.json')
    original_rows = sum(a['physical_rows'] for a in overview)
    structured_rows = sum(a['structured_rows'] for a in overview)
    malformed_rows = sum(a['malformed_rows'] for a in overview)
    save_json(reports / 'malformed_rows_report.json', {'physical_rows': original_rows, 'comma_only_rows': malformed_rows, 'structured_rows': structured_rows, 'files': [{k:a[k] for k in ['file','physical_rows','comma_only_rows','structured_rows']} for a in overview], 'definition': 'Raw columns đều NaN sau read_csv; tính riêng, không đưa vào actual NaN/Inf.'})
    data = pd.concat(frames, ignore_index=True)
    del frames
    if len(data) != structured_rows:
        raise ValueError('Số hàng merge không khớp')
    for c in ['Label','source_day','source_file'] + [c for c in IDENTIFIERS if c in data]:
        data[c] = data[c].astype('category')
    features = [c for c in data if c not in EXCLUDED + IDENTIFIERS]
    conversions = analyze_data_types(data, features)
    save_json(reports / 'datatype_report.json', {'conversions': conversions, 'numeric_features': features, 'categorical_columns': [c for c in data if isinstance(data[c].dtype, pd.CategoricalDtype)], 'metadata': [c for c in IDENTIFIERS if c in data] + ['source_day','source_file'], 'labels': ['Label','binary_label']})
    log_stage('Merge / datatype', original_rows, data)
    merged_columns = len(data.columns)
    missing = analyze_missing_values(data, features).merge(analyze_infinity_values(data, features), on='Feature')
    missing.to_csv(reports / 'missing_inf_report.csv', index=False)
    save_json(reports / 'non_finite_rows.json', {'rows_with_nan': int(data[features].isna().any(axis=1).sum()), 'percentage_rows_with_nan': float(data[features].isna().any(axis=1).mean()*100), 'rows_with_inf': int(data[features].isin([float('inf'),float('-inf')]).any(axis=1).sum()), 'percentage_rows_with_inf': float(data[features].isin([float('inf'),float('-inf')]).any(axis=1).mean()*100)})
    data, non_finite = clean_non_finite_values(data, features, max_fraction)
    log_stage('Actual non finite removal', structured_rows, data)
    all_numeric_features = features
    splits = create_dataset_splits(data)
    validate_dataset_splits(data, splits, features)
    stats_before = split_statistics(splits)
    leakage_raw = check_cross_split_duplicates(splits, features)
    save_json(reports / 'cross_split_duplicate_before_all_numeric.json', leakage_raw)
    logging.info('Leakage before feature removal: %d shared vectors (sum over pairs)', sum(r['Duplicate Feature Rows'] for r in leakage_raw))
    quality = audit_features(splits['train'], features, reports)
    quality['policy'] = 'Khảo sát chỉ trên Train trước row cleanup; chỉ loại constant và exact duplicate columns. Near-constant/correlation không dùng để loại cột.'
    features, selection = select_train_features(splits['train'], features)
    quality['selection'] = selection
    dropped = selection['constant_features_removed'] + [r['removed'] for r in selection['duplicate_features_removed']]
    data = data.drop(columns=dropped)
    splits = {name: frame.drop(columns=dropped) for name,frame in splits.items()}
    duplicate_before = analyze_duplicates(data, features)
    leakage_before = check_cross_split_duplicates(splits, features)
    save_json(reports / 'cross_split_duplicate_before_cleanup.json', leakage_before)
    splits, cleanup = cleanup_split_duplicates(splits, features)
    del data
    data = pd.concat(splits.values(), ignore_index=True)
    duplicate_after = analyze_duplicates(data, features)
    duplicate = {'before': duplicate_before, 'after': duplicate_after, 'cleanup': cleanup}
    save_json(reports / 'duplicate_report.json', duplicate)
    log_stage('Split duplicate/overlap cleanup', non_finite['rows_after'], data)
    save_json(reports / 'feature_quality_report.json', quality)
    save_json(reports / 'feature_columns.json', {'feature_columns': features, 'all_numeric_features': all_numeric_features, 'excluded_columns': EXCLUDED + [c for c in IDENTIFIERS if c in data], 'removed_features': dropped, **selection, 'identifier_exclusion_reason': 'Định danh flow, địa chỉ mạng và thời gian không phải feature numeric; giữ để truy vết.'})
    labels, days = analyze_labels(data)
    labels.to_csv(reports / 'label_distribution.csv', index=False)
    days.to_csv(reports / 'label_distribution_by_day.csv', index=False)
    cleaning = {'original_rows': original_rows, 'physical_rows': original_rows, 'comma_only_rows': malformed_rows, 'structured_rows': structured_rows, 'rows_removed_nan_inf': non_finite['rows_with_nan_or_inf'], 'actual_nan_inf_rows': non_finite['rows_with_nan_or_inf'], 'rows_before_duplicate_cleanup': non_finite['rows_after'], 'rows_removed_duplicates': non_finite['rows_after']-len(data), 'final_rows': len(data), 'original_columns': overview[0]['columns'], 'final_columns': len(data.columns), 'merged_columns': merged_columns, 'non_finite': non_finite, 'deduplication': cleanup, 'split_statistics_before_cleanup': stats_before, **selection}
    save_json(reports / 'cleaning_report.json', cleaning)
    validate_dataset_splits(data, splits, features)
    for name, frame in splits.items():
        log_stage('Split ' + name, len(frame), frame)
    stats = split_statistics(splits)
    save_json(reports / 'split_statistics.json', stats)
    pd.DataFrame([{'Split': name, 'Label': label, 'Count': count} for name,stat in stats.items() for label,count in stat['labels'].items()]).to_csv(reports / 'split_label_distribution.csv', index=False)
    leakage_after = check_cross_split_duplicates(splits, features)
    if any(r['Duplicate Feature Rows'] for r in leakage_after):
        raise ValueError('Overlap model features còn lại sau cleanup')
    leakage = {'before_all_numeric_features': leakage_raw, 'before': leakage_before, 'after': leakage_after, 'cleanup_policy': cleanup}
    save_json(reports / 'cross_split_duplicate_after_cleanup.json', leakage_after)
    save_json(reports / 'cross_split_duplicate_report.json', leakage)
    save_cleaned_dataset(data, output_dir / 'cleaned' / 'cicids2017_cleaned.parquet')
    save_splits(splits, output_dir / 'splits')
    log_stage('Parquet saved', len(data), data)
    # Đọc lại metadata Parquet và từng cột để xác minh file thực sự đã lưu sạch.
    import pyarrow.parquet as pq
    for name,df in splits.items():
        saved = pq.ParquetFile(output_dir / 'splits' / f'{name}.parquet')
        if saved.metadata.num_rows != len(df) or saved.schema_arrow.names != list(df.columns):
            raise ValueError(f'Parquet sai số hàng/schema: {name}')
        for batch in saved.iter_batches(batch_size=65536):
            check = batch.to_pandas()
            if check.isna().any().any() or any(not np.isfinite(check[c]).all() for c in features):
                raise ValueError(f'Parquet còn NaN/Inf: {name}')
    generate_preprocessing_report(reports, overview, schema, conversions, missing, duplicate, quality, cleaning, labels, days, stats, leakage, features)
    summary = {'status': 'PASS', 'raw_rows': original_rows, 'comma_only_rows': malformed_rows, 'structured_rows': structured_rows, 'actual_nan_inf_rows': non_finite['rows_with_nan_or_inf'], 'cleaned_rows': len(data), 'splits': stats, 'nan_remaining': 0, 'inf_remaining': 0, 'non_numeric_model_features': [], 'cross_split_duplicate_count': sum(r['Duplicate Feature Rows'] for r in leakage_after)}
    save_json(reports / 'validation_summary.json', summary)
    print('===============================\nCICIDS2017 PREPROCESSING SUMMARY\n===============================')
    print(f'Raw rows: {original_rows}\nCleaned rows: {len(data)}')
    for name,stat in stats.items():
        print(f'{name.title()}: {stat["total"]}')
    print(f'Train attacks: {stats["train"]["attack"]}\nCalibration attacks: {stats["calibration"]["attack"]}\nNaN remaining: 0\nInf remaining: 0\nNon-numeric model features: []\nCross-split duplicate count: {summary["cross_split_duplicate_count"]}\nPREPROCESSING STATUS: PASS')

def main():
    """Nhận cấu hình đường dẫn và ghi FAIL nếu pipeline dừng."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=ROOT / 'data' / 'raw')
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data')
    parser.add_argument('--reports-dir', type=Path, default=ROOT / 'reports')
    parser.add_argument('--max-non-finite-fraction', type=float, default=.01)
    args = parser.parse_args()
    if not 0 <= args.max_non_finite_fraction <= 1:
        parser.error('max-non-finite-fraction phải nằm trong [0,1]')
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', handlers=[logging.StreamHandler(), logging.FileHandler(args.reports_dir / 'preprocessing.log', encoding='utf-8')])
    try:
        run(args.raw_dir, args.output_dir, args.reports_dir, args.max_non_finite_fraction)
    except Exception as error:
        save_json(args.reports_dir / 'validation_summary.json', {'status': 'FAIL', 'reason': str(error)})
        (args.reports_dir / 'preprocessing_report.md').write_text('# CICIDS2017 preprocessing report\n\nPREPROCESSING STATUS: FAIL\n\n' + str(error) + '\n\nPipeline đã dừng, chưa tạo dataset hoàn tất. Xem dataset_overview.json, schema_report.json, datatype_report.json, missing_inf_report.csv và non_finite_rows.json. Không tự động tăng giới hạn xóa hàng lỗi.\n', encoding='utf-8')
        logging.exception('PREPROCESSING STATUS: FAIL')
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())
