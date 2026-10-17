"""Khảo sát chỉ đọc bốn Parquet để chuẩn bị training, không sửa dữ liệu."""
import hashlib
import logging
from pathlib import Path
import numpy as np
import pandas as pd
import json
from .config import ROOT, EXCLUDED, IDENTIFIERS, SELECTION_DAYS, TEST_DAYS
from .reporting import save_json, table
from .validation import check_cross_split_duplicates
from .feature_audit import analyze_constant_features, analyze_duplicate_columns, analyze_near_constant_features, analyze_correlations

def checksum(path):
    """Tính SHA-256 theo block để tránh nạp toàn bộ file vào RAM."""
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()

def main():
    """Audit trực tiếp dữ liệu đã lưu và xuất báo cáo độc lập."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    reports = ROOT / 'reports'
    output = reports / 'processed_data_audit'
    output.mkdir(parents=True, exist_ok=True)
    features = json.loads((reports / 'feature_columns.json').read_text(encoding='utf-8'))['feature_columns']
    baseline = json.loads((reports / 'notebook_reproduction_report.json').read_text(encoding='utf-8'))['sha256_after']
    previous = json.loads((reports / 'split_statistics.json').read_text(encoding='utf-8'))
    names = ['train','calibration','selection','test']
    paths = {name: ROOT / 'data/splits' / f'{name}.parquet' for name in names}
    before = {name: checksum(path) for name,path in paths.items()}
    splits, summary, label_rows, day_rows, value_rows = {}, [], [], [], []
    errors = []
    expected_days = {'train': {'Monday'}, 'calibration': {'Monday'}, 'selection': set(SELECTION_DAYS), 'test': set(TEST_DAYS)}
    for name,path in paths.items():
        df = pd.read_parquet(path)
        splits[name] = df
        numeric_features = [c for c in df if c not in EXCLUDED + IDENTIFIERS]
        numeric = all(pd.api.types.is_numeric_dtype(df[c]) for c in features)
        nan = int(df[features].isna().sum().sum())
        positive = sum(int(df[c].eq(np.inf).sum()) for c in features)
        negative = sum(int(df[c].eq(-np.inf).sum()) for c in features)
        duplicates = int(df.duplicated(features + ['Label']).sum())
        vectors = int(df.duplicated(features).sum())
        label_consistent = df.binary_label.eq(df.Label.ne('BENIGN').astype('int8')).all()
        days_valid = set(df.source_day.unique()) == expected_days[name]
        checksum_match = before[name] == baseline[path.name]
        summary.append({'Split': name, 'Rows': len(df), 'Columns': len(df.columns), 'Model features': len(features), 'BENIGN': int(df.binary_label.eq(0).sum()), 'ATTACK': int(df.binary_label.eq(1).sum()), 'NaN': nan, '+Inf': positive, '-Inf': negative, 'Feature + Label duplicates': duplicates, 'Feature vector duplicates': vectors, 'RAM MiB': round(df.memory_usage(deep=True).sum()/1024**2,2), 'Disk MiB': round(path.stat().st_size/1024**2,2), 'Checksum matches baseline': checksum_match})
        if not numeric or numeric_features != features or nan or positive or negative or duplicates or not label_consistent or not days_valid or not checksum_match or len(df) != previous[name]['total']:
            errors.append(f'{name}: schema/numeric/finite/duplicate/label/day/checksum/row-count check failed; xem bảng summary')
        if name in ['train','calibration'] and df.binary_label.ne(0).any():
            errors.append(f'{name}: có attack')
        if list(df.columns) != list(splits['train'].columns) or not df.dtypes.equals(splits['train'].dtypes):
            errors.append(f'{name}: schema/dtype khác Train')
        for label,count in df.Label.value_counts().items():
            if count:
                label_rows.append({'Split': name, 'Label': label, 'Count': int(count), 'Percentage': count/len(df)*100})
        for (day,label),count in df.groupby(['source_day','Label'], observed=True).size().items():
            day_rows.append({'Split': name, 'source_day': day, 'Label': label, 'Count': int(count)})
        df[features].describe(percentiles=[.01,.05,.5,.95,.99,.999]).T.to_csv(output / f'{name}_statistics.csv')
        for c in features:
            s = df[c]
            value_rows.append({'Split': name, 'Feature': c, 'dtype': str(s.dtype), 'Negative rows': int(s.lt(0).sum()), 'Zero %': float(s.eq(0).mean()*100), 'Min': s.min(), 'Max': s.max()})
        logging.info('%s: %d rows audited', name, len(df))
    leakage = check_cross_split_duplicates(splits, features)
    if any(row['Duplicate Feature Rows'] for row in leakage):
        errors.append('Còn overlap giữa split')
    train = splits['train']
    constants = [r['Feature'] for r in analyze_constant_features(train, features) if r['Constant']]
    duplicate_columns = analyze_duplicate_columns(train, features)
    near = analyze_near_constant_features(train, features)
    _, correlations = analyze_correlations(train, features)
    if constants or duplicate_columns:
        errors.append('Train còn constant/exact duplicate columns trong model features')
    range_rows = []
    for name,df in splits.items():
        if name == 'train':
            continue
        benign = df.loc[df.binary_label.eq(0)]
        for c in features:
            low,high = train[c].min(), train[c].max()
            outside = benign[c].lt(low) | benign[c].gt(high)
            range_rows.append({'Split': name, 'Feature': c, 'Train min': low, 'Train max': high, 'BENIGN outside Train range': int(outside.sum()), 'BENIGN outside Train range %': float(outside.mean()*100)})
    summary_df = pd.DataFrame(summary)
    labels_df = pd.DataFrame(label_rows)
    ranges = pd.DataFrame(range_rows).sort_values('BENIGN outside Train range %', ascending=False)
    values = pd.DataFrame(value_rows)
    summary_df.to_csv(output / 'split_summary.csv', index=False)
    labels_df.to_csv(output / 'labels.csv', index=False)
    pd.DataFrame(day_rows).to_csv(output / 'labels_by_day.csv', index=False)
    values.to_csv(output / 'feature_value_quality.csv', index=False)
    ranges.to_csv(output / 'benign_range_shift.csv', index=False)
    save_json(output / 'cross_split_duplicates.json', leakage)
    save_json(output / 'train_feature_quality.json', {'constant_features': constants, 'duplicate_columns': duplicate_columns, 'near_constant_features': near, 'highly_correlated_pairs': correlations, 'policy': 'Chỉ khảo sát; không loại thêm feature'})
    after = {name: checksum(path) for name,path in paths.items()}
    if after != before:
        errors.append('Parquet thay đổi trong khi audit')
    attacks = {name: sorted(set(df.loc[df.binary_label.eq(1),'Label'].astype(str))) for name,df in splits.items()}
    unseen = sorted(set(attacks['test']) - set(attacks['selection']))
    negative_values = values.loc[values['Negative rows'] > 0]
    result = {'status': 'FAIL' if errors else 'PASS', 'errors': errors, 'data_unchanged': before == after, 'features': features, 'model_features': len(features), 'split_summary': summary, 'cross_split_duplicates': leakage, 'train_constant_features': constants, 'train_duplicate_columns': duplicate_columns, 'train_near_constant_count': len(near), 'train_high_correlation_pairs': len(correlations), 'test_attack_labels_not_in_selection': unseen, 'sha256': after, 'interpretation': 'PASS xác nhận chất lượng kỹ thuật và reproduction; không bảo đảm hiệu quả model. Số âm, lệch phân phối và nhãn hiếm chỉ được báo cáo, không tự sửa.'}
    save_json(output / 'audit_summary.json', result)
    sections = [
        '# Khảo sát dữ liệu CICIDS2017 đã xử lý',
        f"Trạng thái kỹ thuật: **{result['status']}**. Audit trực tiếp bốn Parquet; không thay preprocessing hoặc dữ liệu. Không train, fit scaler hoặc chọn threshold.",
        '## 1. Schema và chất lượng\n\n' + table(summary_df) + f'\n\nModel có {len(features)} feature numeric. Labels/metadata nằm ngoài model input. Checksum đối chiếu baseline notebook; kiểm tra lại sau audit để xác nhận file không đổi.',
        '## 2. Label distribution\n\n' + table(labels_df) + '\n\nCác attack label có trong Test nhưng không có trong Selection: ' + ', '.join(unseen) + '. Vì khác loại attack theo ngày, kết quả Selection không đại diện đầy đủ cho Test. Labels theo từng nguồn được lưu ở labels_by_day.csv.',
        '## 3. Duplicate và leakage\n\n' + table(pd.DataFrame(leakage)) + '\n\nTrong split: kiểm tra feature + Label và feature vector riêng. Giữa split: dùng function gốc, so sánh exact model-feature vectors, không gồm nhãn hoặc metadata.',
        f'## 4. Feature trên Train\n\nConstant còn lại: {constants}. Duplicate columns còn lại: {duplicate_columns}. Near-constant: {len(near)}; highly correlated pairs: {len(correlations)}. Chỉ khảo sát, giữ nguyên 64 feature hiện tại; xem train_feature_quality.json.',
        '## 5. Giá trị âm và phân phối\n\n' + table(negative_values[['Split','Feature','Negative rows','Min']]) + '\n\nSố âm trong các đại lượng vốn thường không âm cần được xem xét theo ý nghĩa feature; một số trường như cửa sổ TCP có thể dùng giá trị sentinel. Chưa tự loại hoặc thay thế giá trị nào. Xem feature_value_quality.csv và *_statistics.csv; không dùng thống kê này để loại outlier.',
        '## 6. BENIGN khác Train\n\nTop 15 feature/split theo tỷ lệ BENIGN ngoài [min,max] Train:\n\n' + table(ranges.head(15)) + '\n\nĐây là chỉ báo mô tả khác biệt theo ngày, không phải kiểm định drift hoặc anomaly score; không dùng để thay đổi threshold hay dữ liệu. Thống kê ngoài Train chỉ phục vụ khảo sát, không fit biến đổi.',
        '## 7. Chuẩn bị bước tiếp theo\n\n- Lấy đúng danh sách feature_columns từ reports/feature_columns.json.\n- Fit Isolation Forest chỉ trên Train BENIGN; nếu có biến đổi cần fit, chỉ fit trên Train.\n- Calibration BENIGN dùng xác định threshold theo tiêu chí sẽ chọn ở giai đoạn sau.\n- Selection dùng so sánh cấu hình; định nghĩa trước metric, đặc biệt false-positive rate và recall từng attack hiếm.\n- Giữ Test cho đánh giá cuối; không dùng thống kê Test để quyết định feature, cấu hình hoặc threshold.\n- Ghi seed, phiên bản thư viện, danh sách feature, model và threshold để tái lập.\n- Xem xét giá trị âm/sentinel và khác biệt BENIGN theo ngày trước khi chốt thử nghiệm. Thứ tự split là thứ tự CSV, chưa khẳng định timestamp tăng dần.',
        '## 8. Lỗi kiểm tra\n\n' + ('\n'.join(errors) if errors else 'Không phát hiện lỗi kỹ thuật trong các kiểm tra đã chạy.')]
    (output / 'processed_data_audit.md').write_text('\n\n'.join(sections), encoding='utf-8')
    print(json.dumps({k:result[k] for k in ['status','errors','data_unchanged','model_features','train_near_constant_count','train_high_correlation_pairs','test_attack_labels_not_in_selection']}, ensure_ascii=True, indent=2))
    print(summary_df[['Split','Rows','BENIGN','ATTACK']].to_string(index=False))
    return int(bool(errors))

if __name__ == '__main__':
    raise SystemExit(main())
