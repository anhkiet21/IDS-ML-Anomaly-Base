"""Cấu hình nguồn và các nhóm dữ liệu."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = {
    'Monday-WorkingHours.pcap_ISCX.csv': 'Monday',
    'Tuesday-WorkingHours.pcap_ISCX.csv': 'Tuesday',
    'Wednesday-workingHours.pcap_ISCX.csv': 'Wednesday',
    'Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv': 'Thursday-WebAttack',
    'Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv': 'Thursday-Infiltration',
    'Friday-WorkingHours-Morning.pcap_ISCX.csv': 'Friday-Bot',
    'Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv': 'Friday-DDoS',
    'Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv': 'Friday-PortScan',
}
SELECTION_DAYS = list(SOURCES.values())[1:5]
TEST_DAYS = list(SOURCES.values())[5:]
EXCLUDED = ['Label', 'binary_label', 'source_day', 'source_file']
IDENTIFIERS = ['Flow ID', 'Source IP', 'Destination IP', 'Timestamp']
