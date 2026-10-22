class AssessmentService:
    """Scores the complete Wi-Fi troubleshooting journey using recorded evidence."""

    # Weights total 100. These assess learner actions, not whether the incident
    # happened to be technically resolvable.
    RUBRIC = {
        "checked_wifi_status": 10,
        "identified_wifi_disabled": 10,
        "enabled_wifi": 10,
        "verified_wifi_enabled": 10,
        "checked_airplane_mode": 5,
        "checked_corporate_network": 10,
        "checked_incident_scope": 10,
        "checked_authentication": 10,
        "checked_ip_configuration": 5,
        "attempted_reconnection": 10,
        "verified_connectivity": 5,
        "handled_escalation": 5,
    }

    @staticmethod
    def _has_action(action_history: list[dict], action: str) -> bool:
        return any(
            record.get("action") == action and record.get("allowed") is True
            for record in action_history
        )

    def assess(self, action_history: list[dict], incident_status: dict | None = None) -> dict:
        history = action_history or []
        status = incident_status or {}
        score = 0
        feedback = []

        wifi_checks = [
            r for r in history
            if r.get("action") == "check_wifi_status" and r.get("allowed") is True
        ]
        criteria = {
            "checked_wifi_status": bool(wifi_checks),
            "identified_wifi_disabled": any(
                r.get("action") == "check_wifi_status"
                and r.get("finding") == "Wi-Fi enabled: False"
                for r in history
            ),
            "enabled_wifi": any(
                r.get("action") == "enable_wifi" and r.get("allowed") is True
                for r in history
            ),
            "verified_wifi_enabled": any(
                r.get("action") == "check_wifi_status"
                and r.get("finding") == "Wi-Fi enabled: True"
                and any(
                    prior.get("action") == "enable_wifi"
                    and prior.get("sequence_number", 0) < r.get("sequence_number", 0)
                    for prior in history
                )
                for r in history
            ),
            "checked_airplane_mode": self._has_action(history, "check_airplane_mode"),
            "checked_corporate_network": self._has_action(history, "check_corporate_network"),
            "checked_incident_scope": self._has_action(history, "check_incident_scope"),
            "checked_authentication": self._has_action(history, "check_authentication"),
            "checked_ip_configuration": self._has_action(history, "check_ip_configuration"),
            "attempted_reconnection": self._has_action(history, "attempt_reconnect"),
            "verified_connectivity": self._has_action(history, "verify_connectivity"),
            "handled_escalation": bool(
                status.get("escalation_recorded")
                or any(
                    r.get("action") == "escalate_incident"
                    and "Simulated escalation recorded" in str(r.get("finding", ""))
                    for r in history
                )
            ),
        }

        labels = {
            "checked_wifi_status": "Checked Wi-Fi status.",
            "identified_wifi_disabled": "Identified that Wi-Fi was initially disabled.",
            "enabled_wifi": "Performed the Wi-Fi remediation.",
            "verified_wifi_enabled": "Verified Wi-Fi was enabled after remediation.",
            "checked_airplane_mode": "Checked Airplane Mode.",
            "checked_corporate_network": "Checked corporate network visibility.",
            "checked_incident_scope": "Checked whether other employees were affected.",
            "checked_authentication": "Checked for authentication errors.",
            "checked_ip_configuration": "Checked IP configuration.",
            "attempted_reconnection": "Attempted to reconnect to corporate Wi-Fi.",
            "verified_connectivity": "Performed an explicit connectivity verification.",
            "handled_escalation": "Recorded the required simulated escalation.",
        }

        for criterion, weight in self.RUBRIC.items():
            if criteria[criterion]:
                score += weight
                feedback.append(labels[criterion])
            else:
                feedback.append(f"Missing required step: {labels[criterion]}")

        connectivity_restored = bool(status.get("connectivity_restored"))
        escalation_required = bool(status.get("escalation_required"))
        escalation_recorded = bool(status.get("escalation_recorded"))

        if connectivity_restored:
            incident_outcome = "RESOLVED"
            feedback.append("Connectivity was explicitly verified as restored.")
        elif escalation_recorded:
            incident_outcome = "UNRESOLVED_ESCALATED"
            feedback.append("Incident remains unresolved; simulated escalation was recorded.")
        elif escalation_required:
            incident_outcome = "UNRESOLVED_ESCALATION_REQUIRED"
            feedback.append("Incident remains unresolved and escalation is still required.")
        else:
            incident_outcome = status.get("incident_status", "IN_PROGRESS")

        # Mandatory gate: the learner cannot advance without an explicit
        # connectivity verification and either verified resolution or recorded escalation.
        mandatory_criteria_met = (
            criteria["checked_wifi_status"]
            and criteria["checked_airplane_mode"]
            and criteria["checked_corporate_network"]
            and criteria["checked_incident_scope"]
            and criteria["checked_authentication"]
            and criteria["checked_ip_configuration"]
            and criteria["attempted_reconnection"]
            and criteria["verified_connectivity"]
            and (connectivity_restored or escalation_recorded)
        )

        return {
            "score": score,
            "maximum_score": sum(self.RUBRIC.values()),
            "feedback": feedback,
            "criteria": criteria,
            "incident_outcome": incident_outcome,
            "connectivity_restored": connectivity_restored,
            "escalation_required": escalation_required,
            "escalation_recorded": escalation_recorded,
            "mandatory_criteria_met": mandatory_criteria_met,
        }
