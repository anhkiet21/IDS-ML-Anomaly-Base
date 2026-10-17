# CICIDS2017 preprocessing report

PASS: kiểm tra nhãn, ngày, numeric và hữu hạn đã hoàn tất. Không train, scale, chọn threshold hoặc loại outlier.

## Dataset overview

| file | physical_rows | comma_only_rows | structured_rows | columns | benign | attack | nan | positive_inf | negative_inf | duplicate | memory_bytes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Monday-WorkingHours.pcap_ISCX.csv | 529918 | 0 | 529918 | 85 | 529918 | 0 | 64 | 810 | 0 | 34 | 407014993 |
| Tuesday-WorkingHours.pcap_ISCX.csv | 445909 | 0 | 445909 | 85 | 432074 | 13835 | 201 | 327 | 0 | 4 | 339862969 |
| Wednesday-workingHours.pcap_ISCX.csv | 692703 | 0 | 692703 | 85 | 440031 | 252672 | 1008 | 1586 | 0 | 17 | 527496238 |
| Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv | 458968 | 288602 | 170366 | 85 | 168186 | 2180 | 20 | 250 | 0 | 1 | 130021990 |
| Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv | 288602 | 0 | 288602 | 85 | 288566 | 36 | 18 | 396 | 0 | 142 | 219889571 |
| Friday-WorkingHours-Morning.pcap_ISCX.csv | 191033 | 0 | 191033 | 85 | 189067 | 1966 | 28 | 216 | 0 | 2 | 145657218 |
| Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv | 225745 | 0 | 225745 | 85 | 97718 | 128027 | 4 | 64 | 0 | 2 | 170960282 |
| Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv | 286467 | 0 | 286467 | 85 | 127537 | 158930 | 15 | 727 | 0 | 1 | 218100615 |

Physical rows = số record dữ liệu đọc từ CSV, không tính header; comma-only/malformed = mọi raw columns đều NaN, loại ngay sau read_csv trước metadata. Structured rows = physical rows − malformed rows.

## Schema analysis

```json
{
  "common_columns": [
    "ACK Flag Count",
    "Active Max",
    "Active Mean",
    "Active Min",
    "Active Std",
    "Average Packet Size",
    "Avg Bwd Segment Size",
    "Avg Fwd Segment Size",
    "Bwd Avg Bulk Rate",
    "Bwd Avg Bytes/Bulk",
    "Bwd Avg Packets/Bulk",
    "Bwd Header Length",
    "Bwd IAT Max",
    "Bwd IAT Mean",
    "Bwd IAT Min",
    "Bwd IAT Std",
    "Bwd IAT Total",
    "Bwd PSH Flags",
    "Bwd Packet Length Max",
    "Bwd Packet Length Mean",
    "Bwd Packet Length Min",
    "Bwd Packet Length Std",
    "Bwd Packets/s",
    "Bwd URG Flags",
    "CWE Flag Count",
    "Destination IP",
    "Destination Port",
    "Down/Up Ratio",
    "ECE Flag Count",
    "FIN Flag Count",
    "Flow Bytes/s",
    "Flow Duration",
    "Flow IAT Max",
    "Flow IAT Mean",
    "Flow IAT Min",
    "Flow IAT Std",
    "Flow ID",
    "Flow Packets/s",
    "Fwd Avg Bulk Rate",
    "Fwd Avg Bytes/Bulk",
    "Fwd Avg Packets/Bulk",
    "Fwd Header Length",
    "Fwd Header Length.1",
    "Fwd IAT Max",
    "Fwd IAT Mean",
    "Fwd IAT Min",
    "Fwd IAT Std",
    "Fwd IAT Total",
    "Fwd PSH Flags",
    "Fwd Packet Length Max",
    "Fwd Packet Length Mean",
    "Fwd Packet Length Min",
    "Fwd Packet Length Std",
    "Fwd Packets/s",
    "Fwd URG Flags",
    "Idle Max",
    "Idle Mean",
    "Idle Min",
    "Idle Std",
    "Init_Win_bytes_backward",
    "Init_Win_bytes_forward",
    "Label",
    "Max Packet Length",
    "Min Packet Length",
    "PSH Flag Count",
    "Packet Length Mean",
    "Packet Length Std",
    "Packet Length Variance",
    "Protocol",
    "RST Flag Count",
    "SYN Flag Count",
    "Source IP",
    "Source Port",
    "Subflow Bwd Bytes",
    "Subflow Bwd Packets",
    "Subflow Fwd Bytes",
    "Subflow Fwd Packets",
    "Timestamp",
    "Total Backward Packets",
    "Total Fwd Packets",
    "Total Length of Bwd Packets",
    "Total Length of Fwd Packets",
    "URG Flag Count",
    "act_data_pkt_fwd",
    "min_seg_size_forward"
  ],
  "files": [
    {
      "file": "Monday-WorkingHours.pcap_ISCX.csv",
      "missing_columns": [],
      "extra_columns": [],
      "same_order": true,
      "type_mismatch": {}
    },
    {
      "file": "Tuesday-WorkingHours.pcap_ISCX.csv",
      "missing_columns": [],
      "extra_columns": [],
      "same_order": true,
      "type_mismatch": {
        "Bwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Total Length of Fwd Packets": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Min Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Down/Up Ratio": {
          "reference": "float64",
          "actual": "int64"
        },
        "Max Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        }
      }
    },
    {
      "file": "Wednesday-workingHours.pcap_ISCX.csv",
      "missing_columns": [],
      "extra_columns": [],
      "same_order": true,
      "type_mismatch": {
        "Bwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Total Length of Fwd Packets": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Min Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Down/Up Ratio": {
          "reference": "float64",
          "actual": "int64"
        },
        "Max Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        }
      }
    },
    {
      "file": "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
      "missing_columns": [],
      "extra_columns": [],
      "same_order": true,
      "type_mismatch": {
        "Fwd Avg Bytes/Bulk": {
          "reference": "int64",
          "actual": "float64"
        },
        "FIN Flag Count": {
          "reference": "int64",
          "actual": "float64"
        },
        "min_seg_size_forward": {
          "reference": "int64",
          "actual": "float64"
        },
        "Subflow Bwd Bytes": {
          "reference": "int64",
          "actual": "float64"
        },
        "Init_Win_bytes_backward": {
          "reference": "int64",
          "actual": "float64"
        },
        "Fwd PSH Flags": {
          "reference": "int64",
          "actual": "float64"
        },
        "Fwd Header Length.1": {
          "reference": "int64",
          "actual": "float64"
        },
        "Flow Duration": {
          "reference": "int64",
          "actual": "float64"
        },
        "Total Backward Packets": {
          "reference": "int64",
          "actual": "float64"
        },
        "Bwd URG Flags": {
          "reference": "int64",
          "actual": "float64"
        },
        "Fwd Avg Packets/Bulk": {
          "reference": "int64",
          "actual": "float64"
        },
        "ECE Flag Count": {
          "reference": "int64",
          "actual": "float64"
        },
        "Init_Win_bytes_forward": {
          "reference": "int64",
          "actual": "float64"
        },
        "Fwd Header Length": {
          "reference": "int64",
          "actual": "float64"
        },
        "Subflow Fwd Bytes": {
          "reference": "int64",
          "actual": "float64"
        },
        "Total Fwd Packets": {
          "reference": "int64",
          "actual": "float64"
        },
        "Fwd URG Flags": {
          "reference": "int64",
          "actual": "float64"
        },
        "SYN Flag Count": {
          "reference": "int64",
          "actual": "float64"
        },
        "Bwd Avg Bulk Rate": {
          "reference": "int64",
          "actual": "float64"
        },
        "URG Flag Count": {
          "reference": "int64",
          "actual": "float64"
        },
        "RST Flag Count": {
          "reference": "int64",
          "actual": "float64"
        },
        "Subflow Fwd Packets": {
          "reference": "int64",
          "actual": "float64"
        },
        "Subflow Bwd Packets": {
          "reference": "int64",
          "actual": "float64"
        },
        "Bwd PSH Flags": {
          "reference": "int64",
          "actual": "float64"
        },
        "act_data_pkt_fwd": {
          "reference": "int64",
          "actual": "float64"
        },
        "PSH Flag Count": {
          "reference": "int64",
          "actual": "float64"
        },
        "Protocol": {
          "reference": "int64",
          "actual": "float64"
        },
        "Bwd Header Length": {
          "reference": "int64",
          "actual": "float64"
        },
        "Fwd Avg Bulk Rate": {
          "reference": "int64",
          "actual": "float64"
        },
        "Bwd Avg Packets/Bulk": {
          "reference": "int64",
          "actual": "float64"
        },
        "Destination Port": {
          "reference": "int64",
          "actual": "float64"
        },
        "Bwd Avg Bytes/Bulk": {
          "reference": "int64",
          "actual": "float64"
        },
        "ACK Flag Count": {
          "reference": "int64",
          "actual": "float64"
        },
        "Source Port": {
          "reference": "int64",
          "actual": "float64"
        },
        "CWE Flag Count": {
          "reference": "int64",
          "actual": "float64"
        }
      }
    },
    {
      "file": "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
      "missing_columns": [],
      "extra_columns": [],
      "same_order": true,
      "type_mismatch": {
        "Bwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Min Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Down/Up Ratio": {
          "reference": "float64",
          "actual": "int64"
        },
        "Max Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        }
      }
    },
    {
      "file": "Friday-WorkingHours-Morning.pcap_ISCX.csv",
      "missing_columns": [],
      "extra_columns": [],
      "same_order": true,
      "type_mismatch": {
        "Bwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Total Length of Fwd Packets": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Min Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Down/Up Ratio": {
          "reference": "float64",
          "actual": "int64"
        },
        "Max Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        }
      }
    },
    {
      "file": "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
      "missing_columns": [],
      "extra_columns": [],
      "same_order": true,
      "type_mismatch": {
        "Idle Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd IAT Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Flow IAT Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Total Length of Fwd Packets": {
          "reference": "float64",
          "actual": "int64"
        },
        "Active Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd IAT Total": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd IAT Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Active Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Total Length of Bwd Packets": {
          "reference": "float64",
          "actual": "int64"
        },
        "Min Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Down/Up Ratio": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd IAT Total": {
          "reference": "float64",
          "actual": "int64"
        },
        "Idle Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Flow IAT Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd IAT Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd IAT Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Max Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        }
      }
    },
    {
      "file": "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
      "missing_columns": [],
      "extra_columns": [],
      "same_order": true,
      "type_mismatch": {
        "Bwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Total Length of Fwd Packets": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Max": {
          "reference": "float64",
          "actual": "int64"
        },
        "Fwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        },
        "Total Length of Bwd Packets": {
          "reference": "float64",
          "actual": "int64"
        },
        "Min Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Down/Up Ratio": {
          "reference": "float64",
          "actual": "int64"
        },
        "Max Packet Length": {
          "reference": "float64",
          "actual": "int64"
        },
        "Bwd Packet Length Min": {
          "reference": "float64",
          "actual": "int64"
        }
      }
    }
  ],
  "consistent_names": true
}
```

Conversion: []

Pandas phân biệt tên header trùng bằng hậu tố .1; ánh xạ được lưu trong dataset_overview.json. Flow ID, Source IP, Destination IP, Timestamp được giữ làm metadata vì là định danh/thời gian; không dùng làm model input.

## Label distribution

| Label | Count | Percentage |
| --- | --- | --- |
| BENIGN | 2261990 | 80.47043036573297 |
| DoS Hulk | 222563 | 7.917692117776218 |
| PortScan | 158804 | 5.64946185606473 |
| DDoS | 128025 | 4.554497078931809 |
| DoS GoldenEye | 10293 | 0.36617409438348064 |
| FTP-Patator | 7935 | 0.2822881024903254 |
| SSH-Patator | 5897 | 0.20978612985323866 |
| DoS slowloris | 5769 | 0.2052325221508112 |
| DoS Slowhttptest | 5499 | 0.19562725590350338 |
| Bot | 1956 | 0.06958481770271914 |
| Web Attack – Brute Force | 1507 | 0.05361161568404793 |
| Web Attack – XSS | 652 | 0.023194939234239712 |
| Infiltration | 36 | 0.0012807021663077142 |
| Web Attack – Sql Injection | 21 | 0.0007470762636795 |
| Heartbleed | 11 | 0.0003913256619273572 |

| source_day | Label | Count | Percentage |
| --- | --- | --- | --- |
| Friday-Bot | BENIGN | 187498 | 98.96755940756069 |
| Friday-Bot | Bot | 1956 | 1.0324405924393256 |
| Friday-DDoS | BENIGN | 97323 | 43.18786942861707 |
| Friday-DDoS | DDoS | 128025 | 56.81213057138292 |
| Friday-PortScan | BENIGN | 126547 | 44.3478382763684 |
| Friday-PortScan | PortScan | 158804 | 55.6521617236316 |
| Monday | BENIGN | 528082 | 100.0 |
| Thursday-Infiltration | BENIGN | 287226 | 99.98746788645904 |
| Thursday-Infiltration | Infiltration | 36 | 0.012532113540948681 |
| Thursday-WebAttack | BENIGN | 166887 | 98.7105703655947 |
| Thursday-WebAttack | Web Attack – Brute Force | 1507 | 0.8913625958939355 |
| Thursday-WebAttack | Web Attack – Sql Injection | 21 | 0.012421111157115227 |
| Thursday-WebAttack | Web Attack – XSS | 652 | 0.3856459273542442 |
| Tuesday | BENIGN | 430564 | 96.88746073321992 |
| Tuesday | FTP-Patator | 7935 | 1.7855696270893526 |
| Tuesday | SSH-Patator | 5897 | 1.3269696396907262 |
| Wednesday | BENIGN | 437863 | 64.2029742022704 |
| Wednesday | DoS GoldenEye | 10293 | 1.5092419625864006 |
| Wednesday | DoS Hulk | 222563 | 32.633966668523954 |
| Wednesday | DoS Slowhttptest | 5499 | 0.8063073498749262 |
| Wednesday | DoS slowloris | 5769 | 0.8458969087885888 |
| Wednesday | Heartbleed | 11 | 0.0016129079557418058 |

## Missing / Infinity

| Feature | NaN Count | NaN % | +Inf | -Inf | Total Inf |
| --- | --- | --- | --- | --- | --- |
| Flow Bytes/s | 1358 | 0.04797327062188267 | 1509 | 0 | 1509 |
| Flow Packets/s | 0 | 0.0 | 2867 | 0 | 2867 |

{'rows_before': 2830743, 'rows_with_nan_or_inf': 2867, 'percentage_removed': 0.1012808298033414, 'rows_after': 2827876, 'max_fraction': 0.01}

## Duplicate analysis

| Stage | Full duplicates | Feature + Label duplicates | Label conflict groups |
| --- | --- | --- | --- |
| before | 199 | 16918 | 0 |
| after | 0 | 0 | 0 |

| Split | Rows before | Within-split duplicates removed | Overlap rows removed | Rows after |
| --- | --- | --- | --- | --- |
| train | 423584 | 1232 | 0 | 422352 |
| calibration | 105897 | 59 | 108 | 105730 |
| selection | 1595677 | 12860 | 94 | 1582723 |
| test | 702718 | 1255 | 1310 | 700153 |

Không global-dedup trước split. Trong mỗi split giữ hàng đầu theo model features + Label. Giữ conflict khác Label trong cùng split; overlap giữa split được loại bất kể Label theo ưu tiên Train → Calibration → Selection → Test. Chi tiết số hàng và nhãn bị loại: duplicate_report.json.

## Feature quality

Chỉ khảo sát và quyết định trên Train trước cleanup. Numeric features cuối: 64. Constant features removed: ['Bwd PSH Flags', 'Fwd URG Flags', 'Bwd URG Flags', 'CWE Flag Count', 'Fwd Avg Bytes/Bulk', 'Fwd Avg Packets/Bulk', 'Fwd Avg Bulk Rate', 'Bwd Avg Bytes/Bulk', 'Bwd Avg Packets/Bulk', 'Bwd Avg Bulk Rate']. Duplicate features removed: [{'removed': 'SYN Flag Count', 'retained': 'Fwd PSH Flags'}, {'removed': 'Fwd Header Length.1', 'retained': 'Fwd Header Length'}, {'removed': 'Subflow Fwd Packets', 'retained': 'Total Fwd Packets'}, {'removed': 'Subflow Fwd Bytes', 'retained': 'Total Length of Fwd Packets'}, {'removed': 'Subflow Bwd Packets', 'retained': 'Total Backward Packets'}, {'removed': 'Subflow Bwd Bytes', 'retained': 'Total Length of Bwd Packets'}]. Near-constant: 12; high correlation pairs: 40; chỉ report, không xóa hai nhóm này. Chi tiết: feature_quality_report.json, basic_statistics.csv và correlation_matrix.csv (Train).

## Cleaning result

Physical rows 3119345 → loại comma-only 288602 → structured rows 2830743 → actual NaN/Inf rows loại 2867 → split trước cleanup 2827876 → duplicate/overlap rows loại 16918 → final rows 2810958

## Dataset splitting

Monday BENIGN: 80% đầu Train, 20% cuối Calibration, tính sau NaN/Inf cleaning và trước dedup; không shuffle hoặc re-split sau cleanup. Tuesday/Wednesday/Thursday → Selection. Friday → Test. Số hàng trước cleanup: {"train": {"sources": ["Monday"], "source": "Monday", "total": 423584, "benign": 423584, "attack": 0, "labels": {"BENIGN": 423584, "Bot": 0, "DDoS": 0, "DoS GoldenEye": 0, "DoS Hulk": 0, "DoS Slowhttptest": 0, "DoS slowloris": 0, "FTP-Patator": 0, "Heartbleed": 0, "Infiltration": 0, "PortScan": 0, "SSH-Patator": 0, "Web Attack – Brute Force": 0, "Web Attack – Sql Injection": 0, "Web Attack – XSS": 0}}, "calibration": {"sources": ["Monday"], "source": "Monday", "total": 105897, "benign": 105897, "attack": 0, "labels": {"BENIGN": 105897, "Bot": 0, "DDoS": 0, "DoS GoldenEye": 0, "DoS Hulk": 0, "DoS Slowhttptest": 0, "DoS slowloris": 0, "FTP-Patator": 0, "Heartbleed": 0, "Infiltration": 0, "PortScan": 0, "SSH-Patator": 0, "Web Attack – Brute Force": 0, "Web Attack – Sql Injection": 0, "Web Attack – XSS": 0}}, "selection": {"sources": ["Thursday-Infiltration", "Thursday-WebAttack", "Tuesday", "Wednesday"], "source": null, "total": 1595677, "benign": 1327906, "attack": 267771, "labels": {"BENIGN": 1327906, "DoS Hulk": 230124, "DoS GoldenEye": 10293, "FTP-Patator": 7935, "SSH-Patator": 5897, "DoS slowloris": 5796, "DoS Slowhttptest": 5499, "Web Attack – Brute Force": 1507, "Web Attack – XSS": 652, "Infiltration": 36, "Web Attack – Sql Injection": 21, "Heartbleed": 11, "Bot": 0, "DDoS": 0, "PortScan": 0}}, "test": {"sources": ["Friday-Bot", "Friday-DDoS", "Friday-PortScan"], "source": null, "total": 702718, "benign": 413933, "attack": 288785, "labels": {"BENIGN": 413933, "PortScan": 158804, "DDoS": 128025, "Bot": 1956, "DoS GoldenEye": 0, "DoS Hulk": 0, "DoS Slowhttptest": 0, "DoS slowloris": 0, "FTP-Patator": 0, "Heartbleed": 0, "Infiltration": 0, "SSH-Patator": 0, "Web Attack – Brute Force": 0, "Web Attack – Sql Injection": 0, "Web Attack – XSS": 0}}}

## Leakage analysis

### Before cleanup (all raw numeric features)

| Dataset A | Dataset B | Duplicate Feature Rows | matching_rows_a | matching_rows_b | percentage_a | percentage_b |
| --- | --- | --- | --- | --- | --- | --- |
| train | calibration | 108 | 264 | 112 | 0.06232530029462869 | 0.10576314720908053 |
| train | selection | 64 | 217 | 619 | 0.05122950819672131 | 0.038792311977925355 |
| train | test | 26 | 172 | 178 | 0.04060587746468233 | 0.02533021781141226 |
| calibration | selection | 32 | 32 | 279 | 0.030218042059737295 | 0.017484741586173143 |
| calibration | test | 19 | 20 | 80 | 0.01888627628733581 | 0.011384367555690902 |
| selection | test | 1275 | 4430 | 2359 | 0.27762510833959503 | 0.3356965382984355 |

### Before cleanup (final model features)

| Dataset A | Dataset B | Duplicate Feature Rows | matching_rows_a | matching_rows_b | percentage_a | percentage_b |
| --- | --- | --- | --- | --- | --- | --- |
| train | calibration | 108 | 264 | 112 | 0.06232530029462869 | 0.10576314720908053 |
| train | selection | 64 | 217 | 619 | 0.05122950819672131 | 0.038792311977925355 |
| train | test | 26 | 172 | 178 | 0.04060587746468233 | 0.02533021781141226 |
| calibration | selection | 32 | 32 | 279 | 0.030218042059737295 | 0.017484741586173143 |
| calibration | test | 19 | 20 | 80 | 0.01888627628733581 | 0.011384367555690902 |
| selection | test | 1275 | 4430 | 2359 | 0.27762510833959503 | 0.3356965382984355 |

### After cleanup (final model features)

| Dataset A | Dataset B | Duplicate Feature Rows | matching_rows_a | matching_rows_b | percentage_a | percentage_b |
| --- | --- | --- | --- | --- | --- | --- |
| train | calibration | 0 | 0 | 0 | 0.0 | 0.0 |
| train | selection | 0 | 0 | 0 | 0.0 | 0.0 |
| train | test | 0 | 0 | 0 | 0.0 | 0.0 |
| calibration | selection | 0 | 0 | 0 | 0.0 | 0.0 |
| calibration | test | 0 | 0 | 0 | 0.0 | 0.0 |
| selection | test | 0 | 0 | 0 | 0.0 | 0.0 |

Duplicate Feature Rows = số vector duy nhất chung; matching_rows và tỷ lệ tính riêng cho mỗi phía. Hash chỉ lọc ứng viên; mọi overlap được xác nhận bằng so sánh đủ model features, không gồm Label/metadata.

## Final dataset

| Split | Rows | BENIGN | ATTACK |
| --- | --- | --- | --- |
| train | 422352 | 422352 | 0 |
| calibration | 105730 | 105730 | 0 |
| selection | 1582723 | 1322540 | 260183 |
| test | 700153 | 411368 | 288785 |