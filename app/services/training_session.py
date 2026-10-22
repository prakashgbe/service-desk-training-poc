from app.services.scenario_engine import WifiScenarioEngine
from app.services.progress_tracker import ProgressTracker


class TrainingSession:
    """Coordinates actions, evidence, and authoritative incident status."""

    def __init__(self, scenario_id: str):
        self.engine = WifiScenarioEngine(scenario_id)
        self.progress_tracker = ProgressTracker(self.engine.state.scenario_id)

    def perform_action(self, action: str) -> dict:
        action_result = self.engine.execute_action(action)
        if not action_result["allowed"]:
            return {
                "scenario_id": self.engine.state.scenario_id,
                "action_result": action_result,
                "business_rule_result": None,
                "evidence": None,
                "incident_status": self.get_status(),
            }

        rule_result = self.engine.evaluate_finding(action)
        evidence = self.progress_tracker.record_action(
            action, action_result, rule_result
        )
        return {
            "scenario_id": self.engine.state.scenario_id,
            "action_result": action_result,
            "business_rule_result": rule_result,
            "evidence": evidence,
            "incident_status": self.get_status(),
        }

    def get_progress(self) -> list[dict]:
        return self.progress_tracker.get_action_history()

    def get_status(self) -> dict:
        state = self.engine.state
        return {
            "scenario_id": state.scenario_id,
            "incident_status": state.incident_status,
            "connectivity_restored": state.connectivity_restored,
            "reconnection_attempted": state.reconnection_attempted,
            "escalation_required": state.escalation_required,
            "escalation_recorded": state.escalation_recorded,
        }
