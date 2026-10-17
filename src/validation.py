"""Kiểm tra hữu hạn, ngày, nhãn và overlap chính xác giữa split."""
from itertools import combinations
import numpy as np
import pandas as pd
from .config import SELECTION_DAYS, TEST_DAYS

def validate_dataset_splits(data, splits, features):
    """Raise nếu vi phạm bất kỳ điều kiện PASS nào."""
    expected = {'train': {'Monday'}, 'calibration': {'Monday'}, 'selection': set(SELECTION_DAYS), 'test': set(TEST_DAYS)}
    if not features or any(not pd.api.types.is_numeric_dtype(data[c]) for c in features):
        raise ValueError('Feature model không numeric hoặc danh sách rỗng')
    if data.isna().any().any() or any(not np.isfinite(data[c]).all() for c in features):
        raise ValueError('NaN/Inf còn lại')
    for name,df in splits.items():
        if set(df.source_day.unique()) != expected[name] or df.empty:
            raise ValueError(f'Ngày không đúng hoặc split rỗng: {name}')
        if name in ['train', 'calibration'] and (df.binary_label.ne(0).any() or df.Label.ne('BENIGN').any()):
            raise ValueError(f'Attack trong {name}')
    if sum(map(len, splits.values())) != len(data):
        raise ValueError('Split không bao phủ toàn bộ dữ liệu; kiểm tra Monday attack')

def vector_hashes(df, features):
    """Hash chỉ lọc ứng viên; chuẩn hóa dấu zero để không bỏ sót -0 == 0."""
    hashes = np.zeros(len(df), dtype='uint64')
    for c in features:
        values = df[c].mask(df[c].eq(0), 0)
        hashes = hashes * np.uint64(1099511628211) ^ pd.util.hash_pandas_object(values, index=False).to_numpy()
    return hashes

def exact_overlap(left, right, features, left_hash, right_hash):
    """So sánh đầy đủ vector sau khi lọc bằng hash, không coi hash là bằng chứng."""
    candidate_a = np.isin(left_hash, right_hash)
    candidate_b = np.isin(right_hash, left_hash)
    if not candidate_a.any():
        return left.iloc[:0][features]
    return left.loc[candidate_a, features].drop_duplicates().merge(right.loc[candidate_b, features].drop_duplicates(), on=features, how='inner')

def check_cross_split_duplicates(splits, features):
    """Đếm vector chung và số hàng khớp ở cả hai phía bằng so sánh chính xác."""
    hashes = {name: vector_hashes(df, features) for name,df in splits.items()}
    result = []
    for a,b in combinations(splits, 2):
        overlap = exact_overlap(splits[a], splits[b], features, hashes[a], hashes[b])
        counts = []
        for name in [a,b]:
            candidates = np.isin(hashes[name], vector_hashes(overlap, features)) if len(overlap) else np.zeros(len(splits[name]), dtype=bool)
            counts.append(len(splits[name].loc[candidates, features].merge(overlap, on=features, how='inner')) if len(overlap) else 0)
        result.append({'Dataset A': a, 'Dataset B': b, 'Duplicate Feature Rows': len(overlap), 'matching_rows_a': counts[0], 'matching_rows_b': counts[1], 'percentage_a': counts[0]/len(splits[a])*100, 'percentage_b': counts[1]/len(splits[b])*100})
    return result

def cleanup_split_duplicates(splits, features):
    """Ưu tiên Train > Calibration > Selection > Test, bỏ overlap bất kể Label."""
    cleaned, history, stats = {}, [], {}
    for name, frame in splits.items():
        before = len(frame)
        current = frame.drop_duplicates(features + ['Label'], keep='first')
        within = before - len(current)
        hash_current = vector_hashes(current, features)
        removals = []
        for prior_name, prior, prior_hash in history:
            overlap = exact_overlap(current, prior, features, hash_current, prior_hash)
            if overlap.empty:
                continue
            candidates = np.flatnonzero(np.isin(hash_current, vector_hashes(overlap, features)))
            # Index vị trí riêng chỉ dùng nội bộ, không ghi vào dataset.
            candidate_frame = current.iloc[candidates][features].copy()
            candidate_frame['_cleanup_position'] = candidates
            matched = candidate_frame.merge(overlap, on=features, how='inner')['_cleanup_position'].to_numpy()
            keep = np.ones(len(current), dtype=bool)
            keep[matched] = False
            removals.append({'overlap_with': prior_name, 'rows_removed': int((~keep).sum()), 'label_distribution_removed': current.loc[~keep, 'Label'].value_counts().to_dict()})
            current = current.loc[keep]
            hash_current = hash_current[keep]
        cleaned[name] = current
        history.append((name, current, hash_current))
        stats[name] = {'rows_before': before, 'within_split_duplicates_removed': within, 'cross_split_rows_removed': sum(r['rows_removed'] for r in removals), 'overlap_removals': removals, 'rows_after': len(current)}
    return cleaned, {'priority': list(splits), 'within_split_policy': 'Giữ hàng đầu theo model features + Label; giữ conflict khác Label trong cùng split.', 'cross_split_policy': 'Giữ split ưu tiên cao, bỏ vector giống nhau khỏi split ưu tiên thấp bất kể Label; không shuffle hoặc phân chia lại Monday.', 'splits': stats}
