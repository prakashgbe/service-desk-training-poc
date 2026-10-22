from app.services.scenario_engine import WifiScenarioEngine
from app.services.progress_tracker import ProgressTracker


class TrainingSession:
    """
    Coordinates a learner's training session.
    """

    def __init__(self, scenario_id: str):
        self.engine = WifiScenarioEngine(scenario_id)

        self.progress_tracker = ProgressTracker(
            self.engine.state.scenario_id
        )

    def perform_action(self, action: str) -> dict:
        """
        Execute a learner action, evaluate the result,
        and record the evidence.
        """

        # Step 1: Execute the action.
        action_result = self.engine.execute_action(action)

        # Step 2: Reject unsupported actions.
        if not action_result["allowed"]:
            return {
                "scenario_id": self.engine.state.scenario_id,
                "action_result": action_result,
                "business_rule_result": None,
                "evidence": None,
            }

        # Step 3: Evaluate the finding.
        rule_result = self.engine.evaluate_finding(action)

        # Step 4: Record the evidence.
        evidence = self.progress_tracker.record_action(
            action,
            action_result,
            rule_result,
        )

        # Step 5: Return a structured response.
        return {
            "scenario_id": self.engine.state.scenario_id,
            "action_result": action_result,
            "business_rule_result": rule_result,
            "evidence": evidence,
        }

    def get_progress(self) -> list[dict]:
        """
        Return the learner's action history.
        """

        return self.progress_tracker.get_action_history()