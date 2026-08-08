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
USE_STORAGE_TYPE = "memory"  # Options: "memory", "sqlite"


# =====================================================================
# 1. DATA ACCESS LAYER
# Keep your existing PatientModel / SQLitePatientModel implementation.
# =====================================================================

class PatientModel:
    """
    Manages volatile in-memory patient data storage and initial data cleaning.
    """

    def __init__(self):
        self.patients = {
            1: {"Glucose": 95, "BMI": 22.5, "Age": 35, "BloodPressure": 118},
            2: {"Glucose": 130, "BMI": 0, "Age": 52, "BloodPressure": 138},
            3: {"Glucose": 165, "BMI": 31.2, "Age": 61, "BloodPressure": 145},
            4: {"Glucose": 110, "BMI": 27.5, "Age": 44, "BloodPressure": 125},
        }
        self.clean_initial_data()

    def clean_initial_data(self):
        valid_bmis = [
            patient["BMI"]
            for patient in self.patients.values()
            if patient["BMI"] > 0
        ]

        median_bmi = statistics.median(valid_bmis)

        for patient in self.patients.values():
            if patient["BMI"] == 0:
                patient["BMI"] = median_bmi

    def get_all_patient_ids(self):
        return list(self.patients.keys())

    def patient_exists(self, patient_id: int) -> bool:
        return patient_id in self.patients

    def get_patient_by_id(self, patient_id: int) -> Dict[str, Any]:
        return self.patients.get(patient_id)

    def update_patient_metrics(self, patient_id: int, updated_metrics: Dict[str, Any]):
        if not self.patient_exists(patient_id):
            return None

        self.patients[patient_id].update(updated_metrics)
        return self.patients[patient_id]

    def get_all_patients_as_dataframe(self):
        rows = []

        for patient_id, profile in self.patients.items():
            row = {"PatientID": patient_id}
            row.update(profile)
            rows.append(row)

        return pd.DataFrame(rows)


class SQLitePatientModel(PatientModel):
    """
    Placeholder for persistent SQLite implementation.
    Keep your existing SQLitePatientModel if already implemented.
    """
    pass


# =====================================================================
# 2. BUSINESS LOGIC LAYER
# Keep this unchanged if already implemented.
# =====================================================================

class ClinicalRiskService:
    """
    Handles clinical decision rules, point scoring, and risk categorization.
    """

    def calculate_risk(self, patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        glucose_score = self.score_glucose(patient_profile["Glucose"])
        bmi_score = self.score_bmi(patient_profile["BMI"])
        age_score = self.score_age(patient_profile["Age"])
        bp_score = self.score_blood_pressure(patient_profile["BloodPressure"])

        total_score = glucose_score + bmi_score + age_score + bp_score
        risk_category = self.categorize_risk(total_score)

        return {
            "MetricScores": {
                "Glucose": glucose_score,
                "BMI": bmi_score,
                "Age": age_score,
                "BloodPressure": bp_score,
            },
            "TotalScore": total_score,
            "RiskCategory": risk_category,
        }

    def score_glucose(self, glucose: float) -> int:
        if glucose < 100:
            return 0
        elif glucose <= 125:
            return 1
        else:
            return 2

    def score_bmi(self, bmi: float) -> int:
        if bmi < 25:
            return 0
        elif bmi < 30:
            return 1
        else:
            return 2

    def score_age(self, age: int) -> int:
        if age < 40:
            return 0
        elif age < 60:
            return 1
        else:
            return 2

    def score_blood_pressure(self, blood_pressure: float) -> int:
        if blood_pressure < 120:
            return 0
        elif blood_pressure < 140:
            return 1
        else:
            return 2

    def categorize_risk(self, total_score: int) -> str:
        if total_score <= 2:
            return "Low Risk"
        elif total_score <= 5:
            return "Moderate Risk"
        else:
            return "High Risk"


# =====================================================================
# 3. PRESENTATION LAYER
# Streamlit GUI replacement for ConsoleView.
# =====================================================================

class StreamlitView:
    """
    Handles layout, modular panels, visual components, and UI state tracking.
    """

    def configure_page(self):
        st.set_page_config(
            page_title="Diabetes Risk Scoring System",
            page_icon="🩺",
            layout="wide"
        )

    def render_header(self):
        st.title("Diabetes Risk Scoring System")
        st.caption("4-Tier Architecture GUI Application")

        if USE_STORAGE_TYPE == "memory":
            st.warning(
                "Running in In-Memory Mode: Data changes are temporary. "
                "Persistent snapshot display is currently unavailable."
            )
        else:
            st.success("Running in SQLite Persistent Mode.")

    def render_architecture_panel(self):
        with st.expander("System Architecture Overview", expanded=False):
            st.markdown(
                """
                **Current GUI Flow**

                ```text
                User
                  → StreamlitView
                  → StreamlitController
                  → ClinicalRiskService
                  → PatientModel / SQLitePatientModel
                ```

                **Layer Responsibilities**

                - **Presentation Layer:** Streamlit visual interface.
                - **Orchestration Layer:** Coordinates user actions and system workflow.
                - **Business Logic Layer:** Calculates clinical risk score and category.
                - **Data Access Layer:** Stores and retrieves patient data.
                """
            )

    def render_patient_selector(self, patient_ids: List[int]) -> int:
        st.subheader("1. Select Patient")

        selected_patient_id = st.selectbox(
            "Choose Patient ID",
            options=patient_ids,
            index=0
        )

        return selected_patient_id

    def render_patient_input_form(self, patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        st.subheader("2. Patient Clinical Profile")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            glucose = st.number_input(
                "Glucose",
                min_value=0.0,
                value=float(patient_profile["Glucose"]),
                step=1.0
            )

        with col2:
            bmi = st.number_input(
                "BMI",
                min_value=0.0,
                value=float(patient_profile["BMI"]),
                step=0.1
            )

        with col3:
            age = st.number_input(
                "Age",
                min_value=0,
                value=int(patient_profile["Age"]),
                step=1
            )

        with col4:
            blood_pressure = st.number_input(
                "Blood Pressure",
                min_value=0.0,
                value=float(patient_profile["BloodPressure"]),
                step=1.0
            )

        return {
            "Glucose": glucose,
            "BMI": bmi,
            "Age": age,
            "BloodPressure": blood_pressure,
        }

    def render_action_buttons(self):
        st.subheader("3. Actions")

        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            save_clicked = st.button("Save Updates", use_container_width=True)

        with col2:
            calculate_clicked = st.button("Calculate Risk", use_container_width=True)

        with col3:
            clear_clicked = st.button("Clear Report", use_container_width=True)

        return save_clicked, calculate_clicked, clear_clicked

    def render_patient_snapshot(self, patients_df: pd.DataFrame):
        st.subheader("Patient Data Snapshot")
        st.dataframe(patients_df, use_container_width=True)

    def render_risk_report(
        self,
        patient_id: int,
        patient_profile: Dict[str, Any],
        risk_result: Dict[str, Any]
    ):
        st.subheader("4. Diagnostic Risk Report")

        category = risk_result["RiskCategory"]

        if category == "Low Risk":
            st.success(f"Risk Category: {category}")
        elif category == "Moderate Risk":
            st.warning(f"Risk Category: {category}")
        else:
            st.error(f"Risk Category: {category}")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Patient ID", patient_id)

        with col2:
            st.metric("Total Risk Score", risk_result["TotalScore"])

        with col3:
            st.metric("Risk Category", category)

        st.markdown("### Clinical Metrics")

        metrics_df = pd.DataFrame(
            [
                {
                    "Metric": "Glucose",
                    "Value": patient_profile["Glucose"],
                    "Score": risk_result["MetricScores"]["Glucose"],
                },
                {
                    "Metric": "BMI",
                    "Value": patient_profile["BMI"],
                    "Score": risk_result["MetricScores"]["BMI"],
                },
                {
                    "Metric": "Age",
                    "Value": patient_profile["Age"],
                    "Score": risk_result["MetricScores"]["Age"],
                },
                {
                    "Metric": "BloodPressure",
                    "Value": patient_profile["BloodPressure"],
                    "Score": risk_result["MetricScores"]["BloodPressure"],
                },
            ]
        )

        st.table(metrics_df)

        st.info(
            "This tool is intended for risk screening support only. "
            "It is not a medical diagnosis."
        )

    def render_footer(self):
        st.divider()
        st.caption(
            "Diabetes Risk Scoring System | GUI version using Streamlit | "
            "Business logic remains isolated in ClinicalRiskService."
        )


# =====================================================================
# 4. ORCHESTRATION LAYER
# New StreamlitController replacement for ConsoleController.
# =====================================================================

class StreamlitController:
    """
    Coordinates GUI workflow between StreamlitView, PatientModel, and ClinicalRiskService.
    """

    def __init__(
        self,
        model: PatientModel,
        service: ClinicalRiskService,
        view: StreamlitView
    ):
        self.model = model
        self.service = service
        self.view = view

    def run(self):
        self.view.configure_page()
        self.view.render_header()
        self.view.render_architecture_panel()

        patient_ids = self.model.get_all_patient_ids()

        if not patient_ids:
            st.error("No patient records are available.")
            return

        selected_patient_id = self.view.render_patient_selector(patient_ids)

        patient_profile = self.model.get_patient_by_id(selected_patient_id)

        if patient_profile is None:
            st.error("Selected patient record could not be found.")
            return

        updated_metrics = self.view.render_patient_input_form(patient_profile)

        save_clicked, calculate_clicked, clear_clicked = self.view.render_action_buttons()

        if save_clicked:
            self.handle_save_updates(selected_patient_id, updated_metrics)

        if calculate_clicked:
            self.handle_calculate_risk(selected_patient_id, updated_metrics)

        if clear_clicked:
            self.handle_clear_report()

        self.view.render_patient_snapshot(self.model.get_all_patients_as_dataframe())

        if "latest_report" in st.session_state:
            report = st.session_state["latest_report"]
            self.view.render_risk_report(
                report["PatientID"],
                report["PatientProfile"],
                report["RiskResult"]
            )

        self.view.render_footer()

    def handle_save_updates(self, patient_id: int, updated_metrics: Dict[str, Any]):
        validated_metrics = self.validate_metric_inputs(updated_metrics)

        if validated_metrics is None:
            return

        updated_profile = self.model.update_patient_metrics(patient_id, validated_metrics)

        if updated_profile is None:
            st.error("Unable to save patient updates.")
            return

        st.success("Patient metrics updated successfully.")

    def handle_calculate_risk(self, patient_id: int, updated_metrics: Dict[str, Any]):
        validated_metrics = self.validate_metric_inputs(updated_metrics)

        if validated_metrics is None:
            return

        patient_profile = self.model.update_patient_metrics(patient_id, validated_metrics)

        if patient_profile is None:
            st.error("Unable to update patient profile before calculation.")
            return

        risk_result = self.service.calculate_risk(patient_profile)

        st.session_state["latest_report"] = {
            "PatientID": patient_id,
            "PatientProfile": patient_profile,
            "RiskResult": risk_result,
        }

        st.success("Risk calculation completed.")

    def handle_clear_report(self):
        if "latest_report" in st.session_state:
            del st.session_state["latest_report"]

        st.info("Report panel cleared.")

    def validate_metric_inputs(self, metrics: Dict[str, Any]):
        try:
            glucose = float(metrics["Glucose"])
            bmi = float(metrics["BMI"])
            age = int(metrics["Age"])
            blood_pressure = float(metrics["BloodPressure"])
        except ValueError:
            st.error("All clinical metrics must be numeric.")
            return None

        if glucose < 0 or bmi < 0 or age < 0 or blood_pressure < 0:
            st.error("Clinical metrics cannot be negative.")
            return None

        return {
            "Glucose": glucose,
            "BMI": bmi,
            "Age": age,
            "BloodPressure": blood_pressure,
        }


# =====================================================================
# TEST SUITE PLACEHOLDER
# Keep your existing RiskAssessmentTestSuite if already implemented.
# =====================================================================

class RiskAssessmentTestSuite:
    """
    Encapsulates unit, end-to-end, and performance test suites.
    """

    def __init__(self, model_factory, service_class):
        self.model_factory = model_factory
        self.service_class = service_class

    def run_all_tiers(self):
        print("Running automated tests...")
        print("Unit tests, E2E tests, and performance tests should run here.")


# =====================================================================
# SYSTEM APPLICATION ENTRY POINT
# =====================================================================

if __name__ == "__main__":
    if RUN_TEST_SUITE:
        db_model_class = SQLitePatientModel if USE_STORAGE_TYPE == "sqlite" else PatientModel
        suite = RiskAssessmentTestSuite(
            model_factory=db_model_class,
            service_class=ClinicalRiskService
        )
        suite.run_all_tiers()
    else:
        db_model = SQLitePatientModel() if USE_STORAGE_TYPE == "sqlite" else PatientModel()
        rules_service = ClinicalRiskService()
        streamlit_view = StreamlitView()

        controller = StreamlitController(
            model=db_model,
            service=rules_service,
            view=streamlit_view
        )

        controller.run()
