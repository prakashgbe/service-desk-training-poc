class AssessmentService:
    """
    Evaluates a learner's Wi-Fi troubleshooting actions.
    """

    RUBRIC = {
        "checked_wifi_status": 20,
        "identified_wifi_disabled": 20,
        "enabled_wifi": 30,
        "verified_wifi_enabled": 30,
    }

    def assess(self, action_history: list[dict]) -> dict:
        """
        Evaluate recorded learner actions against the rubric.
        """

        score = 0
        feedback = []

        # Criterion 1: Did the learner check Wi-Fi status?
        wifi_checks = [
            record
            for record in action_history
            if record.get("action") == "check_wifi_status"
        ]

        if wifi_checks:
            score += self.RUBRIC["checked_wifi_status"]
            feedback.append("Completed a Wi-Fi status check.")
        else:
            feedback.append("Did not check Wi-Fi status.")

        # Criterion 2: Did the learner identify disabled Wi-Fi?
        identified_issue = any(
            record.get("action") == "check_wifi_status"
            and record.get("finding") == "Wi-Fi enabled: False"
            for record in action_history
        )

        if identified_issue:
            score += self.RUBRIC["identified_wifi_disabled"]
            feedback.append("Identified that Wi-Fi was disabled.")
        else:
            feedback.append(
                "Did not establish evidence that Wi-Fi was disabled."
            )

        # Criterion 3: Did the learner enable Wi-Fi?
        enabled_wifi = any(
            record.get("action") == "enable_wifi"
            and record.get("allowed") is True
            and record.get("finding")
            == "Wi-Fi has been enabled in the simulation."
            for record in action_history
        )

        if enabled_wifi:
            score += self.RUBRIC["enabled_wifi"]
            feedback.append("Performed the simulated Wi-Fi remediation.")
        else:
            feedback.append("Did not complete the simulated remediation.")

        # Criterion 4: Did the learner verify Wi-Fi afterward?
        verified_wifi = any(
            record.get("action") == "check_wifi_status"
            and record.get("finding") == "Wi-Fi enabled: True"
            and any(
                previous.get("action") == "enable_wifi"
                and previous.get("allowed") is True
                and previous.get("finding")
                == "Wi-Fi has been enabled in the simulation."
                and previous.get("sequence_number", 0)
                < record.get("sequence_number", 0)
                for previous in action_history
            )
            for record in action_history
        )

        if verified_wifi:
            score += self.RUBRIC["verified_wifi_enabled"]
            feedback.append("Verified that Wi-Fi was enabled afterward.")
        else:
            feedback.append(
                "Did not verify Wi-Fi status after remediation."
            )

        return {
            "score": score,
            "maximum_score": 100,
            "feedback": feedback,
            "criteria": {
                "checked_wifi_status": bool(wifi_checks),
                "identified_wifi_disabled": identified_issue,
                "enabled_wifi": enabled_wifi,
                "verified_wifi_enabled": verified_wifi,
            },
        }