from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from prop_tool import MotorSpec, compute_motor_performance, load_apc_data

DATA_PATH = Path(__file__).resolve().parent.parent / "APC 17x8.pdf"


def test_sample_pdf_parses():
    data = load_apc_data(DATA_PATH)
    assert not data.empty, "Expected the sample dataset to produce rows"
    assert {"rpm", "thrust_n", "torque_nm", "power_w"}.issubset(data.columns)
    # Confirm rows are grouped by RPM blocks
    unique_rpms = data["rpm"].unique()
    assert unique_rpms.size > 1


def test_motor_performance_columns():
    data = load_apc_data(DATA_PATH)
    spec = MotorSpec(
        kv_rpm_per_volt=720.0,
        resistance_ohm=0.05,
        voltage=22.2,
        no_load_current=1.5,
        max_current=65.0,
    )
    performance = compute_motor_performance(data, spec)

    expected_cols = {
        "motor_current_a",
        "motor_voltage_v",
        "motor_power_w",
        "motor_efficiency",
        "feasible",
        "voltage_headroom_v",
    }
    assert expected_cols.issubset(performance.columns)

    # Efficiency should be finite for most operating points
    finite_eff = np.isfinite(performance["motor_efficiency"].to_numpy())
    assert finite_eff.any(), "Expected at least one finite efficiency value"

    # At least one operating point should be feasible with the default spec
    assert performance["feasible"].any(), "No feasible operating points found"
