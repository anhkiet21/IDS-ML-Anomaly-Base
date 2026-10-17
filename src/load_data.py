"""Đọc từng nguồn, khảo sát trước khi chuẩn hóa và merge."""
import csv
import logging
import numpy as np
import pandas as pd
from .config import SOURCES

def load_single_csv(path):
    """Đọc CSV, giữ nguyên giá trị và dùng encoding phù hợp bộ ISCX."""
    return pd.read_csv(path, encoding='cp1252', low_memory=False)

def remove_malformed_rows(df):
    """Loại hàng thiếu toàn bộ raw columns trước metadata và audit NaN/Inf."""
    malformed = df.isna().all(axis=1)
    return df.loc[~malformed], int(malformed.sum())

def normalize_column_names(df):
    """Chỉ loại khoảng trắng; dừng nếu thao tác tạo tên cột trùng."""
    names = df.columns.str.strip()
    if names.duplicated().any():
        raise ValueError(f'Tên cột trùng sau strip: {names[names.duplicated()].tolist()}')
    df.columns = names
    return df

def add_source_metadata(df, filename, day):
    """Bổ sung nguồn và nhãn nhị phân, giữ Label gốc đã strip."""
    # Giữ missing thực sự để bước cleaning loại hàng, tránh biến thành chuỗi 'nan'.
    df['Label'] = df['Label'].astype('string').str.strip().replace('', pd.NA)
    df['binary_label'] = df['Label'].ne('BENIGN').fillna(True).astype('int8')
    df['source_file'] = filename
    df['source_day'] = day

def load_all_datasets(raw_dir):
    """Khảo sát độc lập đủ tám nguồn rồi trả các frame chưa merge."""
    frames, audits = [], []
    for filename, day in SOURCES.items():
        path = raw_dir / filename
        with path.open(encoding='cp1252', newline='') as stream:
            raw_names = next(csv.reader(stream))
        df = load_single_csv(path)
        physical_rows = len(df)
        df, malformed = remove_malformed_rows(df)
        numeric = df.select_dtypes(include='number')
        label = df.iloc[:, [i for i, c in enumerate(raw_names) if c.strip() == 'Label'][0]].astype('string').str.strip().replace('', pd.NA)
        audits.append(dict(file=filename, physical_rows=physical_rows, comma_only_rows=malformed, malformed_rows=malformed, structured_rows=len(df), rows=len(df), columns=len(df.columns), column_names=list(df.columns), raw_column_names=raw_names,
            parser_disambiguated_columns=[{'position': i, 'raw': a, 'parsed': b} for i, (a, b) in enumerate(zip(raw_names, df.columns)) if a != b],
            dtypes={c.strip(): str(t) for c,t in df.dtypes.items()}, memory_bytes=int(df.memory_usage(deep=True).sum()),
            labels=label.value_counts().to_dict(), unique_labels=int(label.nunique()), missing_labels=int(label.isna().sum()), benign=int(label.eq('BENIGN').sum()), attack=int(label.ne('BENIGN').sum()),
            nan=int(df.isna().sum().sum()), positive_inf=int(numeric.eq(np.inf).sum().sum()), negative_inf=int(numeric.eq(-np.inf).sum().sum()), duplicate=int(df.duplicated().sum())))
        normalize_column_names(df)
        add_source_metadata(df, filename, day)
        frames.append(df)
        logging.info('Audit %s: physical rows=%d malformed=%d structured rows=%d memory=%d', filename, physical_rows, malformed, len(df), audits[-1]['memory_bytes'])
    return frames, audits

def validate_schema(frames, audits):
    """So sánh tên, thứ tự và dtype; không âm thầm bỏ cột."""
    reference = [c.strip() for c in audits[0]['column_names']]
    common = set(reference).intersection(*[set(c.strip() for c in a['column_names']) for a in audits])
    report = []
    for a in audits:
        names = [c.strip() for c in a['column_names']]
        report.append(dict(file=a['file'], missing_columns=sorted(set(reference)-set(names)), extra_columns=sorted(set(names)-set(reference)),
            same_order=names == reference, type_mismatch={c: {'reference': audits[0]['dtypes'][c], 'actual': a['dtypes'][c]} for c in common if a['dtypes'][c] != audits[0]['dtypes'][c]}))
    return {'common_columns': sorted(common), 'files': report, 'consistent_names': all(not r['missing_columns'] and not r['extra_columns'] for r in report)}
