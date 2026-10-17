"""Lưu báo cáo theo định dạng có thể kiểm tra lại."""
import json
import numpy as np

def save_json(path, value):
    """Ghi JSON UTF-8 và chuyển scalar numpy sang kiểu Python."""
    def convert(item):
        if isinstance(item, np.generic):
            return item.item()
        raise TypeError(type(item).__name__)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=convert), encoding='utf-8')

def table(frame):
    """Tạo bảng Markdown không cần thư viện bổ sung."""
    rows = [list(frame.columns)] + frame.astype(str).values.tolist()
    return '\n'.join(['| ' + ' | '.join(rows[0]) + ' |', '| ' + ' | '.join(['---'] * len(rows[0])) + ' |'] + ['| ' + ' | '.join(row) + ' |' for row in rows[1:]])
