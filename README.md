# 🏠 Smart Home Real-Time Monitoring System

This project simulates a real-time IoT pipeline for smart home devices using **Apache Kafka** and integrates a machine learning model to detect anomalies or forecast energy usage. It demonstrates how to stream data, perform ML inference, and trigger alerts or forecasts in real time.

---

## 📌 Features

- 📡 Simulates IoT devices like thermostats, motion sensors, and door locks
- 🧠 Integrates a pluggable ML model for anomaly detection or forecasting
- ⚠️ Publishes alerts and predictions to Kafka topics for downstream consumers
- 🔄 Kafka producer and consumer implemented in Python
- 🌐 RESTful interface to serve ML models (e.g., Flask or TensorFlow Serving)

---

## 🧱 Architecture Overview

```text
[ IoT Devices (Simulated) ]
          |
          v
Kafka Topic: smart-home-events
          |
          v
+---------------------+
| Kafka Consumer (Py) |
+---------------------+
          |
          v
  [ ML Model Inference ]
          |
          v
Kafka Topics:
  - anomaly-alerts
  - energy-forecast
          |
          v
[ DB / Dashboard / Notification Service ]
