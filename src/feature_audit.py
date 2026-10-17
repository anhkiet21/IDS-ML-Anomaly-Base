"""Khảo sát chất lượng feature, không tự động chọn hoặc xóa."""
import pandas as pd

def analyze_constant_features(data, features):
    """Lưu số giá trị khác nhau và trạng thái constant."""
    return [{'Feature': c, 'Unique values': int(data[c].nunique()), 'Constant': data[c].nunique() == 1} for c in features]

def analyze_near_constant_features(data, features):
    """Tìm giá trị chiếm ít nhất 99 phần trăm."""
    result = []
    for c in features:
        counts = data[c].value_counts()
        if len(counts) and counts.iloc[0] / len(data) >= .99:
            result.append({'Feature': c, 'Dominant Value': counts.index[0], 'Dominant %': counts.iloc[0] / len(data) * 100})
    return result

def analyze_duplicate_columns(data, features):
    """So sánh giá trị, không phụ thuộc khác biệt int/float."""
    return [{'Feature A': a, 'Feature B': b, 'Identical': True} for i,a in enumerate(features) for b in features[i+1:] if (data[a].to_numpy() == data[b].to_numpy()).all()]

def analyze_correlations(data, features):
    """Tính Pearson và ghi các cặp có trị tuyệt đối từ 0.95."""
    corr = data[features].corr()
    return corr, [{'Feature A': a, 'Feature B': b, 'Correlation': corr.loc[a,b]} for i,a in enumerate(features) for b in features[i+1:] if abs(corr.loc[a,b]) >= .95]

def audit_features(data, features, reports):
    """Tạo báo cáo khảo sát; giữ toàn bộ feature numeric."""
    constants = analyze_constant_features(data, features)
    near = analyze_near_constant_features(data, features)
    duplicates = analyze_duplicate_columns(data, features)
    corr, pairs = analyze_correlations(data, features)
    corr.to_csv(reports / 'correlation_matrix.csv')
    pd.DataFrame(constants).to_csv(reports / 'constant_features.csv', index=False)
    data[features].describe(percentiles=[.01,.05,.25,.5,.75,.95,.99,.999]).T.to_csv(reports / 'basic_statistics.csv')
    return {'constant_features': [r['Feature'] for r in constants if r['Constant']], 'unique_values': constants, 'near_constant_features': near, 'duplicate_features': duplicates, 'highly_correlated_pairs': pairs, 'policy': 'Chỉ khảo sát toàn dataset; không dùng thống kê để fit scaler hoặc loại feature/outlier.'}

def select_train_features(train, features):
    """Chỉ dùng Train để loại constant và giữ cột đầu của nhóm giống nhau."""
    constants = [c for c in features if train[c].nunique() == 1]
    kept, removed = [], []
    for c in features:
        if c in constants:
            continue
        duplicate_of = next((a for a in kept if (train[a].to_numpy() == train[c].to_numpy()).all()), None)
        if duplicate_of is None:
            kept.append(c)
        else:
            removed.append({'removed': c, 'retained': duplicate_of})
    if not kept:
        raise ValueError('Không còn feature sau khi khảo sát Train')
    return kept, {'fit_source': 'train_before_row_cleanup', 'constant_features_removed': constants, 'duplicate_features_removed': removed}
