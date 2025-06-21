
from kafka import KafkaConsumer
import json

# Power profile map
device_power_profile = {
    'door': (5, 1),
    'light': (60, 10),
    'plug': (500, 300),
    'camera': (10, 2)
}

# Kafka Consumer
consumer = KafkaConsumer(
    'smart_home_stream',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    group_id='my-group'
)

print("Listening for messages...")

# Real-time processing loop
for message in consumer:
    data = message.value
    device = data['Device']
    power_usage = data['Power Usage']
    device_reading = data['Device Reading']
    device_status = data['Device Status']

    mean_power, std_dev_power = device_power_profile[device]
    safe_power_min = mean_power - 3 * std_dev_power
    safe_power_max = mean_power + 3 * std_dev_power

    anomaly = "Normal"

    if device_status == 1 and not (safe_power_min <= power_usage <= safe_power_max):
        anomaly = "Abnormal Power Usage"
    elif device_status == 1 and not (20 <= device_reading <= 80):
        anomaly = "Abnormal Device Reading"
    elif device_status == 1 and device_reading == 0:
        anomaly = "ON but No Device Reading"
    elif device_status == 0 and device_reading > 0:
        anomaly = "OFF but Device Reading Active"

    print(f"📡 Received: {data} => 🚨 Anomaly: {anomaly}")