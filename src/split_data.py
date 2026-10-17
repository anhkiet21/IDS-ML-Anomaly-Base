"""Chia theo nguồn, giữ thứ tự Monday và không sampling."""
from .config import SELECTION_DAYS, TEST_DAYS

def create_dataset_splits(data):
    """Chia Monday BENIGN 80/20 và giữ toàn bộ các ngày còn lại."""
    monday = data.loc[data.source_day.eq('Monday') & data.Label.eq('BENIGN')]
    cut = int(len(monday) * .8)
    return {'train': monday.iloc[:cut], 'calibration': monday.iloc[cut:],
        'selection': data.loc[data.source_day.isin(SELECTION_DAYS)], 'test': data.loc[data.source_day.isin(TEST_DAYS)]}

def split_statistics(splits):
    """Thống kê thực tế theo nguồn và nhãn."""
    return {name: {'sources': sorted(df.source_day.unique().tolist()), 'source': 'Monday' if name in ['train','calibration'] else None, 'total': len(df), 'benign': int(df.binary_label.eq(0).sum()), 'attack': int(df.binary_label.eq(1).sum()), 'labels': df.Label.value_counts().to_dict()} for name,df in splits.items()}
