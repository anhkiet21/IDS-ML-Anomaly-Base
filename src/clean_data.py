"""Làm sạch có giới hạn và không dùng thống kê để impute."""
import numpy as np

def clean_non_finite_values(data, features, max_fraction=0.01):
    """Dừng nếu số hàng lỗi vượt giới hạn; không loại outlier."""
    bad = data.isna().any(axis=1)
    for c in features:
        bad |= data[c].isin([np.inf, -np.inf])
    count = int(bad.sum())
    report = {'rows_before': len(data), 'rows_with_nan_or_inf': count, 'percentage_removed': count / len(data) * 100, 'rows_after': len(data)-count, 'max_fraction': max_fraction}
    if count / len(data) > max_fraction:
        raise ValueError(f'Tỷ lệ NaN/Inf bất thường: {report}; xem missing_inf_report.csv')
    # Chỉ thay Inf sau khi đã lưu thống kê nguyên trạng và kiểm tra giới hạn.
    for c in features:
        if data[c].isin([np.inf, -np.inf]).any():
            data[c] = data[c].replace([np.inf, -np.inf], np.nan)
    return data.dropna(), report

def remove_duplicates(data, features):
    """Giữ lần xuất hiện đầu tiên theo thứ tự nguồn ban đầu."""
    result = data.drop_duplicates(subset=features + ['Label'], keep='first')
    return result, {'rows_before': len(data), 'duplicates_removed': len(data)-len(result), 'rows_after': len(result)}
