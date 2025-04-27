import streamlit as st
import pandas as pd
import plotly.express as px
import time

# --- Config
st.set_page_config(page_title="Robot Scent Detection", page_icon="🧟‍♂️", layout="wide")

# --- Title
st.title("🧟‍♂️ Real-Time Robot Scent Detection Dashboard")

# --- Search Bar
scent_search = st.text_input("Search by Scent Event (type 1 for detected, 0 for none)")

# --- Load fake data
@st.cache_data
def load_data():
    return pd.read_csv("fake_robot_sniff_data.csv")

data = load_data()

# --- Initialize session state
if "sensor_df" not in st.session_state:
    st.session_state.sensor_df = pd.DataFrame(columns=["timestamp", "humidity", "temperature", "air_resistance", "event_detected"])
    st.session_state.idx = 0

# --- Placeholder
placeholder = st.empty()

# --- Stream data live
while st.session_state.idx < len(data):

    new_row = data.iloc[st.session_state.idx]
    st.session_state.sensor_df = pd.concat([st.session_state.sensor_df, pd.DataFrame([new_row])])

    with placeholder.container():
        st.markdown("### Live Sensor KPIs")

        if new_row["event_detected"] == 1:
            st.error("🚨 SCENT EVENT DETECTED! 🚨")

        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(label="Humidity (%)", value=f"{new_row['humidity']:.2f}")
        kpi2.metric(label="Temperature (°C)", value=f"{new_row['temperature']:.2f}")
        kpi3.metric(label="Air Resistance", value=f"{new_row['air_resistance']:.2f}")

        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            st.markdown("### Humidity & Temperature Over Time")
            fig = px.line(
                st.session_state.sensor_df,
                x="timestamp",
                y=["humidity", "temperature"],
                labels={"value": "Reading", "timestamp": "Time"},
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)

        with fig_col2:
            st.markdown("### Air Resistance Over Time")
            fig2 = px.line(
                st.session_state.sensor_df,
                x="timestamp",
                y="air_resistance",
                labels={"air_resistance": "Air Resistance", "timestamp": "Time"},
                template="plotly_dark",
                color_discrete_sequence=["cyan"]
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("### Recent Sensor Data")

        # Apply filters
        filtered_df = st.session_state.sensor_df.copy()

        if scent_search:
            try:
                scent_search_val = int(scent_search)
                filtered_df = filtered_df[filtered_df["event_detected"] == scent_search_val]
            except ValueError:
                st.warning("Please enter 0 or 1 for scent search.")

        st.dataframe(filtered_df.tail(20), use_container_width=True)

    st.session_state.idx += 1
    time.sleep(1)
    st.rerun()