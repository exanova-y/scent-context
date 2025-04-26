import pandas as pd
import numpy as np

# --- Parameters ---
n_samples = 1000
np.random.seed(42)  # So your lies are repeatable

# --- Generate fake data ---
timestamps = pd.date_range(start="2025-01-01", periods=n_samples, freq="5S")  # Every 5 seconds

humidity = np.clip(np.random.normal(50, 10, n_samples), 20, 100)
temperature = np.clip(np.random.normal(22, 3, n_samples), -5, 45)
air_resistance = np.clip(np.random.normal(100, 30, n_samples), 30, 300)

# Create "smell events" where humidity and air resistance spike
event_detected = (np.random.rand(n_samples) > 0.9).astype(int)
humidity += event_detected * np.random.normal(20, 5, n_samples)
air_resistance += event_detected * np.random.normal(50, 10, n_samples)

# --- Create DataFrame ---
robot_sniff_df = pd.DataFrame({
    "timestamp": timestamps,
    "humidity": humidity,
    "temperature": temperature,
    "air_resistance": air_resistance,
    "event_detected": event_detected
})

# --- Save to CSV ---
robot_sniff_df.to_csv("fake_robot_sniff_data.csv", index=True)

print("Fake scent detection dataset created: fake_robot_sniff_data.csv")
print(robot_sniff_df.head())
