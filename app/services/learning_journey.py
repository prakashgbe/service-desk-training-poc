class LearningJourneyService:
    """Recommends a next step using score plus mandatory competency gates."""

    def recommend_next_step(self, assessment: dict) -> dict:
        score = assessment.get("score", 0)
        feedback = assessment.get("feedback", [])
        mandatory_met = assessment.get("mandatory_criteria_met", False)

        if score >= 80 and mandatory_met:
            return {
                "recommendation": "ADVANCE",
                "message": (
                    "Good work. You demonstrated the required troubleshooting "
                    "and outcome-handling steps. The incident outcome is recorded separately."
                ),
                "next_step": "WIFI-002",
                "incident_outcome": assessment.get("incident_outcome", "UNKNOWN"),
            }

        if score >= 50:
            return {
                "recommendation": "PRACTICE",
                "message": (
                    "Review the missing troubleshooting or outcome-handling steps, "
                    "then retry this scenario."
                ),
                "next_step": "RETRY_CURRENT_SCENARIO",
                "areas_to_improve": feedback,
                "incident_outcome": assessment.get("incident_outcome", "UNKNOWN"),
            }

        return {
            "recommendation": "REVIEW",
            "message": (
                "Review the approved troubleshooting knowledge before attempting "
                "the scenario again."
            ),
            "next_step": "REVIEW_KNOWLEDGE_AND_RETRY",
            "areas_to_improve": feedback,
            "incident_outcome": assessment.get("incident_outcome", "UNKNOWN"),
        }
