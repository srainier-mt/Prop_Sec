from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class MotorSpec:
    """Electrical parameters describing a BLDC motor."""

    kv_rpm_per_volt: float
    resistance_ohm: float
    voltage: float
    no_load_current: float = 0.0
    max_current: Optional[float] = None

    @property
    def kt_nm_per_amp(self) -> float:
        """Return the torque constant derived from ``Kv``."""

        if self.kv_rpm_per_volt <= 0:
            raise ValueError("kv_rpm_per_volt must be positive")
        return 60.0 / (2.0 * math.pi * self.kv_rpm_per_volt)


def compute_motor_performance(data: pd.DataFrame, spec: MotorSpec) -> pd.DataFrame:
    """Combine APC propeller data with a :class:`MotorSpec`.

    The resulting frame contains additional columns for motor current draw,
    required terminal voltage, and shaft-to-electrical efficiency. A boolean
    ``feasible`` column indicates whether the requested operating point can be
    achieved with the provided supply voltage and current limit.
    """

    if data.empty:
        return data.copy()

    df = data.copy()

    kt = spec.kt_nm_per_amp

    torque_nm = df["torque_nm"].to_numpy()
    mechanical_power = df["power_w"].to_numpy()

    current = torque_nm / kt + spec.no_load_current
    required_voltage = df["rpm"].to_numpy() / spec.kv_rpm_per_volt + current * spec.resistance_ohm

    electrical_power = required_voltage * current
    with np.errstate(divide="ignore", invalid="ignore"):
        motor_efficiency = np.where(electrical_power > 0, mechanical_power / electrical_power, np.nan)

    feasible = required_voltage <= spec.voltage + 1e-6
    if spec.max_current is not None:
        feasible &= current <= spec.max_current + 1e-6

    df["motor_current_a"] = current
    df["motor_voltage_v"] = required_voltage
    df["motor_power_w"] = electrical_power
    df["motor_efficiency"] = motor_efficiency
    df["feasible"] = feasible
    df["voltage_headroom_v"] = spec.voltage - required_voltage

    return df
