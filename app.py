import streamlit as st
from kafka import KafkaConsumer
import json
import time
import pandas as pd
from collections import Counter

# Page config
st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

st.title("📡 Smart Home Real-Time Stream")
st.caption("Live anomaly detection and device monitoring from Kafka topic `smart_home_stream`")

# Kafka consumer setup
@st.cache_resource
def get_consumer():
    return KafkaConsumer(
        'smart_home_stream',
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        group_id='streamlit-app-group'
    )

# Device power thresholds
device_power_profile = {
    'door': (5, 1),
    'light': (60, 10),
    'plug': (500, 300),
    'camera': (10, 2)
}

def detect_anomaly(device, power, reading, status):
    mean_power, std_dev = device_power_profile[device]
    min_power = mean_power - 3 * std_dev
    max_power = mean_power + 3 * std_dev

    if status == 1 and not (min_power <= power <= max_power):
        return "Abnormal Power Usage"
    elif status == 1 and not (20 <= reading <= 80):
        return "Abnormal Device Reading"
    elif status == 1 and reading == 0:
        return "ON but No Device Reading"
    elif status == 0 and reading > 0:
        return "OFF but Device Reading Active"
    return "Normal"

# App state
consumer = get_consumer()
device_filter = st.selectbox("🔌 Filter by device", ["All", "door", "light", "plug", "camera"])
anomaly_counter = Counter()
anomaly_records = []

# Line chart state
power_usage_history = {
    "door": [],
    "light": [],
    "plug": [],
    "camera": []
}
chart_window = 50

# Streamlit placeholders
line_chart = st.empty()
anomaly_chart = st.empty()
table_container = st.empty()
download_button = st.empty()

# Main streaming loop
for msg in consumer:
    data = msg.value
    device = data['Device']

    if device_filter != "All" and device != device_filter:
        continue

    anomaly = detect_anomaly(
        device,
        data['Power Usage'],
        data['Device Reading'],
        data['Device Status']
    )

    status_str = "ON" if data["Device Status"] == 1 else "OFF"

    row = {
        "Timestamp": data["Timestamp"],
        "Device": device,
        "Power Usage": data["Power Usage"],
        "Device Reading": data["Device Reading"],
        "Device Status": status_str,
        "Anomaly": anomaly
    }

    # Add to anomaly table if needed
    if anomaly != "Normal":
        anomaly_records.append(row)
        anomaly_counter[anomaly] += 1

    # Update power history
    power_usage_history[device].append(data["Power Usage"])
    if len(power_usage_history[device]) > chart_window:
        power_usage_history[device].pop(0)

    # Live line chart
    chart_df = pd.DataFrame({
        d: power_usage_history[d] for d in (power_usage_history.keys() if device_filter == "All" else [device_filter])
    })
    line_chart.line_chart(chart_df)

    # Anomaly bar chart
    bar_df = pd.DataFrame.from_dict(anomaly_counter, orient='index', columns=["Count"])
    anomaly_chart.bar_chart(bar_df)

    # Table of latest anomalies
    if anomaly_records:
        df_anomalies = pd.DataFrame(anomaly_records[-50:])
        table_container.dataframe(df_anomalies, use_container_width=True)

        csv = pd.DataFrame(anomaly_records).to_csv(index=False).encode('utf-8')
        download_button.download_button(
            label="⬇️ Download anomalies as CSV",
            data=csv,
            file_name='anomalies.csv',
            mime='text/csv'
        )

    time.sleep(0.2)