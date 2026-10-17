# IDS Anomaly Base

Dự án phát hiện bất thường trong lưu lượng mạng bằng Isolation Forest.

- `data/raw/`: dữ liệu gốc.
- `data/processed/`: dữ liệu sau xử lý.
- `notebooks/`: notebook phân tích và huấn luyện.
- `models/`: mô hình đã lưu.
- `results/`: kết quả đánh giá.

Chạy `start_notebook.bat` để mở JupyterLab tại thư mục dự án.

## Pipeline tiền xử lý CICIDS2017

Khảo sát lại các split đã lưu bằng `python -m src.audit_processed`.
Báo cáo độc lập tại `reports/processed_data_audit/processed_data_audit.md` gồm
schema, nhãn, NaN/Inf, duplicate/leakage, checksum, giá trị âm và phân phối BENIGN
so với Train. Lệnh này không sửa dataset, fit scaler hoặc train model.

Notebook trình bày và tái chạy pipeline: `notebooks/01_CICIDS2017_Preprocessing.ipynb`.
Chọn kernel Python có dependency của dự án, rồi **Restart Kernel → Run All**.
Notebook gọi nguyên `src.run_preprocessing.run()` một lần ở phần 4, sau đó trình bày
các báo cáo vừa sinh theo 20 phần và kiểm tra trực tiếp bốn Parquet ở phần 19.
Không đổi thuật toán hoặc chính sách hiện tại trong `src/`. Assertions giữ baseline:
Train 422.352, Calibration 105.730, Selection 1.582.723, Test 700.153 và overlap bằng 0.
Nếu không khớp, notebook dừng; không tự điều chỉnh baseline.

Cài dependency bằng `python -m pip install -r requirements.txt`, sau đó chạy tại thư mục dự án:

```powershell
python -m src.run_preprocessing
python -m unittest discover -s tests -v
```

Pipeline đọc riêng 8 CSV trong `data/raw/`, loại hàng raw trống toàn bộ trước metadata và trước audit NaN/Inf, kiểm tra schema, chuyển numeric có báo lỗi, thống kê NaN/+Inf/-Inf thật rồi replace Inf và dropna. Sau đó chia theo ngày, kiểm tra leakage trước cleanup, loại constant/duplicate columns dựa trên Train, cleanup duplicate trong split và overlap giữa split, rồi lưu:

- `data/cleaned/cicids2017_cleaned.parquet`
- `data/splits/train.parquet`
- `data/splits/calibration.parquet`
- `data/splits/selection.parquet`
- `data/splits/test.parquet`
- `reports/preprocessing_report.md` và các báo cáo JSON/CSV.

Monday BENIGN chia 80% đầu / 20% cuối sau NaN/Inf cleaning, trước dedup; không shuffle hoặc re-split sau cleanup. Selection dùng Tuesday–Thursday; Test dùng Friday. Constant và exact duplicate columns chỉ quyết định trên Train trước row cleanup; near-constant và correlation chỉ report. Không huấn luyện, scaling, PCA, sampling, impute hoặc loại outlier.

Bản CSV có Flow ID, Source IP, Destination IP và Timestamp: giữ trong dataset như metadata nhưng không đưa vào model input. Khi training sau này, lấy danh sách `feature_columns` từ `reports/feature_columns.json`; không lấy tất cả cột ngoài Label. Pandas phân biệt header trùng bằng `.1`; ánh xạ tên raw/parser được ghi trong overview.

Mặc định dừng nếu hơn 1% structured rows có NaN/Inf thật; malformed/comma-only rows được báo riêng. Có thể tùy chỉnh `--raw-dir`, `--output-dir`, `--reports-dir`. Leakage được kiểm tra trên cả all numeric features và final model features trước row cleanup; lưu riêng before/after.

Chính sách cleanup: trong mỗi split giữ lần xuất hiện đầu theo model features + Label; giữ conflict khác Label trong cùng split. Giữa split, ưu tiên Train → Calibration → Selection → Test, loại vector giống nhau khỏi split ưu tiên thấp hơn bất kể Label. Các số hàng và nhãn bị loại được lưu. Hash chỉ lọc ứng viên, mọi overlap được xác nhận bằng vector đầy đủ. PASS yêu cầu không còn overlap trên final model features. `data/cleaned/` lưu hợp của bốn split cuối.
