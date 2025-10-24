"""Utilities for analyzing APC propulsion data."""
from .parser import load_apc_data
from .analysis import MotorSpec, compute_motor_performance

__all__ = [
    "load_apc_data",
    "MotorSpec",
    "compute_motor_performance",
]
