"""Khảo sát kiểu dữ liệu, giá trị thiếu, vô hạn và duplicate."""
import numpy as np
import pandas as pd

def analyze_data_types(data, features):
    """Ghi rõ giá trị lỗi trước khi chuyển các feature sang numeric."""
    reports = []
    for col in features:
        if not pd.api.types.is_numeric_dtype(data[col]):
            original = data[col]
            converted = pd.to_numeric(original, errors='coerce')
            failed = original.notna() & converted.isna()
            reports.append({'feature': col, 'original_dtype': str(original.dtype), 'conversion_failed': int(failed.sum()), 'invalid_values': original[failed].astype(str).value_counts().to_dict()})
            data[col] = converted
    return reports

def analyze_missing_values(data, features):
    """Đếm NaN trên từng feature và từng hàng."""
    counts = data[features].isna().sum()
    return pd.DataFrame({'Feature': features, 'NaN Count': counts.values, 'NaN %': counts.values / len(data) * 100}).sort_values('NaN Count', ascending=False)

def analyze_infinity_values(data, features):
    """Đếm riêng hai dấu vô hạn."""
    return pd.DataFrame([{'Feature': c, '+Inf': int(data[c].eq(np.inf).sum()), '-Inf': int(data[c].eq(-np.inf).sum()), 'Total Inf': int(data[c].abs().eq(np.inf).sum())} for c in features])

def analyze_duplicates(data, features):
    """Phát hiện xung đột Label trên vector feature giống nhau chính xác."""
    subset = data.loc[data.duplicated(features, keep=False), features + ['Label']]
    conflicts = []
    if len(subset):
        groups = subset.groupby(features, sort=False, dropna=False, observed=True)['Label']
        for _, labels in groups:
            unique = sorted(labels.unique().tolist())
            if len(unique) > 1:
                conflicts.append({'number_of_identical_feature_vectors': len(labels), 'different_labels': unique})
    return {'full_duplicates': int(data.duplicated([c for c in data if c not in ['source_file', 'source_day']]).sum()),
        'feature_label_duplicates': int(data.duplicated(features + ['Label']).sum()), 'conflict_groups': len(conflicts), 'label_conflicts': conflicts,
        'conflict_policy': 'Giữ xung đột; chỉ xóa vector feature + Label giống nhau.'}
