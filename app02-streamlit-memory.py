import sqlite3
import statistics
import time
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd
import streamlit as st


# =====================================================================
# CONFIGURATION SWITCHES
# =====================================================================
RUN_TEST_SUITE = False
RUN_IN_CONSOLE = False
USE_STORAGE_TYPE = "sqlite"  # Options: "sqlite" | "memory"


# =====================================================================
# 1. DATA ACCESS LAYER (MODELS)
# =====================================================================
class PatientModel:
    """Manages volatile in-memory patient data storage and initial data cleaning."""
    
    def __init__(self):
        self._raw_patients: Dict[int, Dict[str, float]] = {
            101: {"Glucose": 95.0, "BMI": 22.5, "Age": 28.0, "BloodPressure": 115.0},
            102: {"Glucose": 145.0, "BMI": 0.0, "Age": 54.0, 
