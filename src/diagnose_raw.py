"""Khảo sát cấu trúc CSV lỗi mà không sửa dữ liệu nguồn."""
import csv
from collections import Counter
from .config import ROOT, IDENTIFIERS
from .reporting import save_json

def diagnose(path):
    """Đếm hàng trống và mẫu cột còn giá trị trên hàng thiếu toàn bộ numeric."""
    blank = missing_label = bad = rows = 0
    first = last = None
    patterns = Counter()
    with path.open(encoding='cp1252', newline='') as stream:
        reader = csv.reader(stream)
        header = [c.strip() for c in next(reader)]
        label = header.index('Label')
        numeric = [i for i,c in enumerate(header) if c not in IDENTIFIERS + ['Label']]
        widths = Counter()
        for line,row in enumerate(reader, 2):
            rows += 1
            widths[len(row)] += 1
            if len(row) != len(header):
                continue
            if not any(v.strip() for v in row):
                blank += 1
                first = first or line
                last = line
            missing_label += not row[label].strip()
            if all(not row[i].strip() for i in numeric):
                bad += 1
                patterns.update([tuple(header[i] for i,v in enumerate(row) if v.strip())])
    return {'file': path.name, 'rows': rows, 'expected_columns': len(header), 'row_width_counts': dict(widths), 'all_empty_rows': blank, 'first_empty_line': first, 'last_empty_line': last, 'missing_label_rows': missing_label, 'all_numeric_empty_rows': bad, 'nonempty_column_patterns': [{'columns': list(k), 'count': v} for k,v in patterns.items()]}

if __name__ == '__main__':
    result = diagnose(ROOT / 'data/raw/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv')
    save_json(ROOT / 'reports/raw_csv_structure.json', result)
    print(result)
