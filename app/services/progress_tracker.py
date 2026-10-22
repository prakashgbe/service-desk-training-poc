from datetime import datetime, timezone


class ProgressTracker:
    """
    Records learner actions during a training scenario.
    """

    def __init__(self, scenario_id: str):
        self.scenario_id = scenario_id
        self.action_history = []

    def record_action(
        self,
        action: str,
        action_result: dict,
        rule_result: dict,
    ) -> dict:
        """
        Record an action, its finding, and its business rule evaluation.
        """

        record = {
            "scenario_id": self.scenario_id,
            "sequence_number": len(self.action_history) + 1,
            "action": action,
            "allowed": action_result.get("allowed", False),
            "finding": action_result.get("finding"),
            "finding_type": rule_result.get("finding_type"),
            "priority": rule_result.get("priority"),
            "recommendation": rule_result.get("recommendation"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        self.action_history.append(record)

        return record

    def get_action_history(self) -> list[dict]:
        """
        Return all recorded learner actions in sequence.
        """

        return self.action_history.copy()