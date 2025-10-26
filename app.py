from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from prop_tool import MotorSpec, compute_motor_performance, load_apc_data

st.set_page_config(page_title="APC Propulsion Analyzer", layout="wide")
st.title("APC Propulsion Analyzer")

st.markdown(
    """
Upload an APC performance file (`.dat` or the generated PDF report), provide your
motor's electrical characteristics, and inspect propulsion efficiency metrics
across the available RPM set points. A sample 17×8 APC data set is bundled and
loaded automatically if no file is uploaded.
"""
)

with st.sidebar:
    st.header("Motor specifications")
    kv = st.number_input("Kv (RPM/V)", min_value=100.0, max_value=5000.0, value=720.0, step=10.0)
    resistance = st.number_input("Resistance (Ω)", min_value=0.0, value=0.05, step=0.005, format="%.4f")
    voltage = st.number_input("Supply voltage (V)", min_value=1.0, value=22.2, step=0.1)
    no_load_current = st.number_input("No-load current (A)", min_value=0.0, value=1.5, step=0.1)
    max_current = st.number_input("Max current (A)", min_value=0.0, value=60.0, step=1.0)
    enforce_current_limit = st.checkbox("Enforce max current", value=True)

uploaded = st.file_uploader("APC performance file", type=["dat", "txt", "pdf"])

if uploaded is not None:
    data = load_apc_data(uploaded)
    st.success(f"Loaded {uploaded.name} with {data['rpm'].nunique()} RPM blocks.")
else:
    default_path = Path(__file__).resolve().parent / "APC 17x8.pdf"
    data = load_apc_data(default_path)
    st.info("Using bundled APC 17×8 sample data.")

if data.empty:
    st.warning("No datapoints found in the provided file.")
    st.stop()

spec = MotorSpec(
    kv_rpm_per_volt=kv,
    resistance_ohm=resistance,
    voltage=voltage,
    no_load_current=no_load_current,
    max_current=max_current if enforce_current_limit else None,
)

performance = compute_motor_performance(data, spec)

available_rpms = np.sort(performance["rpm"].unique())
selected_rpm = st.selectbox("Propeller RPM", available_rpms.tolist(), index=len(available_rpms) - 1)

rpm_frame = performance[performance["rpm"] == selected_rpm].reset_index(drop=True)
feasible_frame = rpm_frame[rpm_frame["feasible"]]

cols = st.columns(3)

if not feasible_frame.empty:
    best_eff = feasible_frame.loc[feasible_frame["motor_efficiency"].idxmax()]
    cols[0].metric("Peak motor efficiency", f"{best_eff['motor_efficiency']*100:.1f}%", help="Highest shaft-to-electrical efficiency for the selected RPM")
    max_thrust = feasible_frame["thrust_n"].max()
    cols[1].metric("Max thrust", f"{max_thrust:.1f} N")
    max_current_draw = feasible_frame["motor_current_a"].max()
    cols[2].metric("Max current draw", f"{max_current_draw:.1f} A")
else:
    cols[0].warning("No feasible operating points with the current spec")

st.subheader("Performance tables")
st.dataframe(rpm_frame[[
    "mph",
    "thrust_n",
    "thrust_lbf",
    "motor_current_a",
    "motor_voltage_v",
    "motor_power_w",
    "motor_efficiency",
    "prop_efficiency",
    "feasible",
]])

st.subheader("Visualisations")
if not rpm_frame.empty:
    fig, axes = plt.subplots(1, 3, figsize=(18, 4))

    axes[0].plot(rpm_frame["mph"], rpm_frame["thrust_n"], marker="o", label="Thrust")
    axes[0].set_xlabel("Airspeed (mph)")
    axes[0].set_ylabel("Thrust (N)")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(rpm_frame["mph"], rpm_frame["motor_current_a"], marker="o", color="tab:orange", label="Current")
    if enforce_current_limit and max_current > 0:
        axes[1].axhline(max_current, linestyle="--", color="tab:red", alpha=0.4, label="Limit")
    axes[1].set_xlabel("Airspeed (mph)")
    axes[1].set_ylabel("Current (A)")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(rpm_frame["mph"], rpm_frame["motor_efficiency"] * 100.0, marker="o", color="tab:green", label="Motor η")
    axes[2].plot(rpm_frame["mph"], rpm_frame["prop_efficiency"] * 100.0, marker="o", color="tab:blue", label="Prop η")
    axes[2].set_xlabel("Airspeed (mph)")
    axes[2].set_ylabel("Efficiency (%)")
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()

    plt.tight_layout()
    st.pyplot(fig)

st.caption("Motor terminal voltage is calculated from Kv, winding resistance, and the torque required to produce the tabulated thrust.")
