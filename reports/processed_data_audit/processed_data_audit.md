# Khảo sát dữ liệu CICIDS2017 đã xử lý

Trạng thái kỹ thuật: **PASS**. Audit trực tiếp bốn Parquet; không thay preprocessing hoặc dữ liệu. Không train, fit scaler hoặc chọn threshold.

## 1. Schema và chất lượng

| Split | Rows | Columns | Model features | BENIGN | ATTACK | NaN | +Inf | -Inf | Feature + Label duplicates | Feature vector duplicates | RAM MiB | Disk MiB | Checksum matches baseline |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| train | 422352 | 72 | 64 | 422352 | 0 | 0 | 0 | 0 | 0 | 0 | 260.63 | 68.33 | True |
| calibration | 105730 | 72 | 64 | 105730 | 0 | 0 | 0 | 0 | 0 | 0 | 101.8 | 16.38 | True |
| selection | 1582723 | 72 | 64 | 1322540 | 260183 | 0 | 0 | 0 | 0 | 0 | 842.71 | 201.5 | True |
| test | 700153 | 72 | 64 | 411368 | 288785 | 0 | 0 | 0 | 0 | 0 | 399.98 | 77.81 | True |

Model có 64 feature numeric. Labels/metadata nằm ngoài model input. Checksum đối chiếu baseline notebook; kiểm tra lại sau audit để xác nhận file không đổi.

## 2. Label distribution

| Split | Label | Count | Percentage |
| --- | --- | --- | --- |
| train | BENIGN | 422352 | 100.0 |
| calibration | BENIGN | 105730 | 100.0 |
| selection | BENIGN | 1322540 | 83.56105269210089 |
| selection | DoS Hulk | 222563 | 14.062031069239534 |
| selection | DoS GoldenEye | 10293 | 0.6503348975152317 |
| selection | FTP-Patator | 7935 | 0.5013511524126458 |
| selection | SSH-Patator | 5897 | 0.37258572725612754 |
| selection | DoS slowloris | 5769 | 0.3644983992777005 |
| selection | DoS Slowhttptest | 5499 | 0.347439191823206 |
| selection | Web Attack – Brute Force | 1507 | 0.09521565049601226 |
| selection | Web Attack – XSS | 652 | 0.0411948268901128 |
| selection | Infiltration | 36 | 0.0022745609939326086 |
| selection | Web Attack – Sql Injection | 21 | 0.0013268272464606883 |
| selection | Heartbleed | 11 | 0.0006950047481460748 |
| test | BENIGN | 411368 | 58.75401519382192 |
| test | PortScan | 158804 | 22.681328223973903 |
| test | DDoS | 128025 | 18.285289072531288 |
| test | Bot | 1956 | 0.27936750967288576 |

Các attack label có trong Test nhưng không có trong Selection: Bot, DDoS, PortScan. Vì khác loại attack theo ngày, kết quả Selection không đại diện đầy đủ cho Test. Labels theo từng nguồn được lưu ở labels_by_day.csv.

## 3. Duplicate và leakage

| Dataset A | Dataset B | Duplicate Feature Rows | matching_rows_a | matching_rows_b | percentage_a | percentage_b |
| --- | --- | --- | --- | --- | --- | --- |
| train | calibration | 0 | 0 | 0 | 0.0 | 0.0 |
| train | selection | 0 | 0 | 0 | 0.0 | 0.0 |
| train | test | 0 | 0 | 0 | 0.0 | 0.0 |
| calibration | selection | 0 | 0 | 0 | 0.0 | 0.0 |
| calibration | test | 0 | 0 | 0 | 0.0 | 0.0 |
| selection | test | 0 | 0 | 0 | 0.0 | 0.0 |

Trong split: kiểm tra feature + Label và feature vector riêng. Giữa split: dùng function gốc, so sánh exact model-feature vectors, không gồm nhãn hoặc metadata.

## 4. Feature trên Train

Constant còn lại: []. Duplicate columns còn lại: []. Near-constant: 2; highly correlated pairs: 22. Chỉ khảo sát, giữ nguyên 64 feature hiện tại; xem train_feature_quality.json.

## 5. Giá trị âm và phân phối

| Split | Feature | Negative rows | Min |
| --- | --- | --- | --- |
| train | Flow Duration | 14 | -1.0 |
| train | Flow Bytes/s | 9 | -12000000.0 |
| train | Flow Packets/s | 14 | -2000000.0 |
| train | Flow IAT Mean | 14 | -1.0 |
| train | Flow IAT Max | 14 | -1.0 |
| train | Flow IAT Min | 497 | -14.0 |
| train | Fwd Header Length | 21 | -1929349973.0 |
| train | Bwd Header Length | 17 | -167770490.0 |
| train | Init_Win_bytes_forward | 158908 | -1.0 |
| train | Init_Win_bytes_backward | 228582 | -1.0 |
| train | min_seg_size_forward | 21 | -83885313.0 |
| calibration | Flow Duration | 1 | -1.0 |
| calibration | Flow Packets/s | 1 | -2000000.0 |
| calibration | Flow IAT Mean | 1 | -1.0 |
| calibration | Flow IAT Max | 1 | -1.0 |
| calibration | Flow IAT Min | 15 | -3.0 |
| calibration | Fwd Header Length | 2 | -1006623756.0 |
| calibration | Init_Win_bytes_forward | 64549 | -1.0 |
| calibration | Init_Win_bytes_backward | 68970 | -1.0 |
| calibration | min_seg_size_forward | 2 | -83885313.0 |
| selection | Flow Duration | 53 | -4.0 |
| selection | Flow Bytes/s | 30 | -261000000.0 |
| selection | Flow Packets/s | 53 | -2000000.0 |
| selection | Flow IAT Mean | 53 | -4.0 |
| selection | Flow IAT Max | 53 | -4.0 |
| selection | Flow IAT Min | 1869 | -14.0 |
| selection | Fwd IAT Min | 11 | -8.0 |
| selection | Fwd Header Length | 12 | -32212234632.0 |
| selection | Bwd Header Length | 5 | -1073741320.0 |
| selection | Init_Win_bytes_forward | 583013 | -1.0 |
| selection | Init_Win_bytes_backward | 844437 | -1.0 |
| selection | min_seg_size_forward | 12 | -536870661.0 |
| test | Flow Duration | 47 | -13.0 |
| test | Flow Bytes/s | 46 | -193000000.0 |
| test | Flow Packets/s | 47 | -2000000.0 |
| test | Flow IAT Mean | 47 | -13.0 |
| test | Flow IAT Max | 47 | -13.0 |
| test | Flow IAT Min | 509 | -13.0 |
| test | Fwd IAT Min | 6 | -12.0 |
| test | Init_Win_bytes_forward | 186769 | -1.0 |
| test | Init_Win_bytes_backward | 280970 | -1.0 |

Số âm trong các đại lượng vốn thường không âm cần được xem xét theo ý nghĩa feature; một số trường như cửa sổ TCP có thể dùng giá trị sentinel. Chưa tự loại hoặc thay thế giá trị nào. Xem feature_value_quality.csv và *_statistics.csv; không dùng thống kê này để loại outlier.

## 6. BENIGN khác Train

Top 15 feature/split theo tỷ lệ BENIGN ngoài [min,max] Train:

| Split | Feature | Train min | Train max | BENIGN outside Train range | BENIGN outside Train range % |
| --- | --- | --- | --- | --- | --- |
| test | Fwd IAT Total | 0.0 | 119999987.0 | 968 | 0.2353124209953132 |
| selection | Fwd IAT Total | 0.0 | 119999987.0 | 2905 | 0.21965309177794246 |
| test | Bwd IAT Total | 0.0 | 119999643.0 | 494 | 0.12008712393769083 |
| selection | Bwd IAT Total | 0.0 | 119999643.0 | 1427 | 0.10789843785443162 |
| test | Flow IAT Max | -1.0 | 119999735.0 | 61 | 0.014828571984208786 |
| test | Fwd IAT Max | 0.0 | 119999869.0 | 60 | 0.014585480640205364 |
| selection | Fwd IAT Max | 0.0 | 119999869.0 | 165 | 0.012475993164667987 |
| selection | Flow IAT Max | -1.0 | 119999735.0 | 154 | 0.011644260287023455 |
| test | Idle Mean | 0.0 | 119999735.0 | 39 | 0.009480562416133487 |
| test | Idle Max | 0.0 | 119999735.0 | 39 | 0.009480562416133487 |
| test | Idle Min | 0.0 | 119999735.0 | 39 | 0.009480562416133487 |
| test | Bwd IAT Max | 0.0 | 119974145.0 | 37 | 0.00899437972812664 |
| selection | Idle Min | 0.0 | 119999735.0 | 103 | 0.007788044217944259 |
| selection | Idle Mean | 0.0 | 119999735.0 | 103 | 0.007788044217944259 |
| selection | Idle Max | 0.0 | 119999735.0 | 103 | 0.007788044217944259 |

Đây là chỉ báo mô tả khác biệt theo ngày, không phải kiểm định drift hoặc anomaly score; không dùng để thay đổi threshold hay dữ liệu. Thống kê ngoài Train chỉ phục vụ khảo sát, không fit biến đổi.

## 7. Chuẩn bị bước tiếp theo

- Lấy đúng danh sách feature_columns từ reports/feature_columns.json.
- Fit Isolation Forest chỉ trên Train BENIGN; nếu có biến đổi cần fit, chỉ fit trên Train.
- Calibration BENIGN dùng xác định threshold theo tiêu chí sẽ chọn ở giai đoạn sau.
- Selection dùng so sánh cấu hình; định nghĩa trước metric, đặc biệt false-positive rate và recall từng attack hiếm.
- Giữ Test cho đánh giá cuối; không dùng thống kê Test để quyết định feature, cấu hình hoặc threshold.
- Ghi seed, phiên bản thư viện, danh sách feature, model và threshold để tái lập.
- Xem xét giá trị âm/sentinel và khác biệt BENIGN theo ngày trước khi chốt thử nghiệm. Thứ tự split là thứ tự CSV, chưa khẳng định timestamp tăng dần.

## 8. Lỗi kiểm tra

Không phát hiện lỗi kỹ thuật trong các kiểm tra đã chạy.