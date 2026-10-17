"""Kiểm thử các quy tắc có thể gây mất dữ liệu hoặc leakage."""
import unittest
import tempfile
from unittest.mock import patch
from pathlib import Path
import numpy as np
import pandas as pd
from src.clean_data import clean_non_finite_values, remove_duplicates
from src.data_audit import analyze_data_types, analyze_duplicates
from src.split_data import create_dataset_splits
from src.validation import check_cross_split_duplicates, validate_dataset_splits, cleanup_split_duplicates
from src.config import SOURCES
from src.load_data import add_source_metadata, remove_malformed_rows
from src.feature_audit import select_train_features
from src.run_preprocessing import run

class PreprocessingTests(unittest.TestCase):
    """Kiểm tra bằng dữ liệu nhỏ có lỗi và xung đột cố ý."""
    def test_conversion_and_guard(self):
        """Phải báo giá trị lỗi và dừng trước khi loại quá nhiều hàng."""
        df = pd.DataFrame({'x': ['1', 'bad', 'inf']})
        report = analyze_data_types(df, ['x'])
        self.assertEqual(report[0]['conversion_failed'], 1)
        with self.assertRaises(ValueError):
            clean_non_finite_values(df, ['x'])
        clean, report = clean_non_finite_values(df, ['x'], 1)
        self.assertEqual(len(clean), 1)
        self.assertEqual(report['rows_with_nan_or_inf'], 2)

    def test_malformed_before_metadata(self):
        """Chỉ loại hàng trống toàn bộ; NaN của record thật vẫn được thống kê."""
        raw = pd.DataFrame({'x': [np.nan, np.nan, 2], 'Label': [None, 'BENIGN', 'BENIGN']})
        structured, count = remove_malformed_rows(raw)
        self.assertEqual(count, 1)
        self.assertEqual(len(structured), 2)
        self.assertEqual(int(structured.x.isna().sum()), 1)

    def test_train_only_feature_removal(self):
        """Cột constant và duplicate được quyết định từ Train, giữ thứ tự cột."""
        train = pd.DataFrame({'x': [1,2,3], 'same_x': [1,2,3], 'constant': [0,0,0], 'other': [2,1,4]})
        kept, report = select_train_features(train, list(train))
        self.assertEqual(kept, ['x','other'])
        self.assertEqual(report['constant_features_removed'], ['constant'])
        self.assertEqual(report['duplicate_features_removed'], [{'removed': 'same_x', 'retained': 'x'}])

    def test_overlap_before_after_and_priority(self):
        """Overlap khác Label và signed zero phải bị loại ở split thấp hơn."""
        def frame(values, labels):
            return pd.DataFrame({'x': values, 'Label': labels})
        splits = {'train': frame([0.,1.,1.], ['BENIGN']*3), 'calibration': frame([-0.,2.], ['BENIGN']*2), 'selection': frame([1.,3.], ['Bot','BENIGN']), 'test': frame([3.,4.], ['Bot','BENIGN'])}
        before = check_cross_split_duplicates(splits, ['x'])
        self.assertGreater(sum(r['Duplicate Feature Rows'] for r in before), 0)
        cleaned, report = cleanup_split_duplicates(splits, ['x'])
        self.assertEqual(cleaned['train'].x.tolist(), [0.,1.])
        self.assertEqual(cleaned['calibration'].x.tolist(), [2.])
        self.assertEqual(cleaned['selection'].x.tolist(), [3.])
        self.assertEqual(cleaned['test'].x.tolist(), [4.])
        self.assertEqual(report['splits']['train']['within_split_duplicates_removed'], 1)
        self.assertEqual(sum(r['Duplicate Feature Rows'] for r in check_cross_split_duplicates(cleaned, ['x'])), 0)

    def test_hash_collision_does_not_create_overlap(self):
        """Hash trùng không được coi hai vector khác nhau là duplicate."""
        splits = {'train': pd.DataFrame({'x': [1.,2.], 'Label': ['BENIGN']*2}), 'test': pd.DataFrame({'x': [3.,4.], 'Label': ['Bot']*2})}
        with patch('src.validation.vector_hashes', side_effect=lambda df, features: np.zeros(len(df), dtype='uint64')):
            report = check_cross_split_duplicates(splits, ['x'])
            self.assertEqual(report[0]['Duplicate Feature Rows'], 0)
            cleaned, _ = cleanup_split_duplicates(splits, ['x'])
            self.assertEqual(len(cleaned['test']), 2)

    def test_missing_label_stays_missing(self):
        """Label thiếu không được chuyển thành chuỗi rồi giữ lại như attack."""
        df = pd.DataFrame({'x': [1,2,3], 'Label': [' BENIGN ', None, ' ']})
        add_source_metadata(df, 'a.csv', 'Monday')
        self.assertEqual(int(df.Label.isna().sum()), 2)
        clean, _ = clean_non_finite_values(df, ['x'], 1)
        self.assertEqual(clean.Label.tolist(), ['BENIGN'])

    def test_conflicts_and_metadata(self):
        """Metadata không che duplicate; khác nhãn phải được giữ lại."""
        df = pd.DataFrame({'x': [1,1,1,2], 'Label': ['BENIGN','BENIGN','Bot','BENIGN'], 'binary_label': [0,0,1,0], 'source_file': ['a','b','c','a'], 'source_day': ['Monday','Tuesday','Friday-Bot','Monday']})
        report = analyze_duplicates(df, ['x'])
        self.assertEqual(report['conflict_groups'], 1)
        clean, _ = remove_duplicates(df, ['x'])
        self.assertEqual(len(clean), 3)
        self.assertEqual(clean.iloc[0].source_day, 'Monday')
        overlap = check_cross_split_duplicates({'train': clean.iloc[[0]], 'test': clean.iloc[[1]]}, ['x'])
        self.assertEqual(overlap[0]['Duplicate Feature Rows'], 1)

    def test_days_order_and_attack_guard(self):
        """Monday không shuffle; mọi ngày đúng và attack bị chặn."""
        days = ['Monday'] * 10 + list(SOURCES.values())[1:]
        df = pd.DataFrame({'x': np.arange(len(days)), 'source_day': days, 'Label': 'BENIGN', 'binary_label': np.int8(0)})
        splits = create_dataset_splits(df)
        validate_dataset_splits(df, splits, ['x'])
        self.assertEqual(splits['train'].x.tolist(), list(range(8)))
        self.assertEqual(splits['calibration'].x.tolist(), [8,9])
        splits['train'] = splits['train'].copy()
        splits['train'].loc[0, 'binary_label'] = 1
        with self.assertRaises(ValueError):
            validate_dataset_splits(df, splits, ['x'])

    def test_end_to_end_parquet(self):
        """Kiểm tra pipeline đầy đủ và đọc lại bốn file Parquet trên fixture riêng."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = root / 'raw'
            raw.mkdir()
            offset = 0
            for filename,day in SOURCES.items():
                size = 10 if day == 'Monday' else 2
                pd.DataFrame({' x ': np.arange(offset, offset+size), 'constant': 0, ' Label': ['BENIGN'] * size}).to_csv(raw / filename, index=False)
                offset += size
            run(raw, root / 'data', root / 'reports', .01)
            counts = {name: len(pd.read_parquet(root / 'data/splits' / f'{name}.parquet')) for name in ['train','calibration','selection','test']}
            self.assertEqual(counts, {'train': 8, 'calibration': 2, 'selection': 8, 'test': 6})
            self.assertTrue((root / 'reports/preprocessing_report.md').exists())

if __name__ == '__main__':
    unittest.main()
