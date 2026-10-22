class LearningJourneyService:
    """Recommends the learner's next step based on assessment results."""

    def recommend_next_step(self, assessment: dict) -> dict:
        score = assessment["score"]
        feedback = assessment["feedback"]

        if score >= 80:
            return {
                "recommendation": "ADVANCE",
                "message": (
                    "Good work! You are ready to attempt "
                    "a more challenging troubleshooting scenario."
                ),
                "next_step": "WIFI-002",
            }

        if score >= 50:
            return {
                "recommendation": "PRACTICE",
                "message": (
                    "Review the assessment feedback and practise "
                    "the troubleshooting steps you missed."
                ),
                "next_step": "RETRY_CURRENT_SCENARIO",
                "areas_to_improve": feedback,
            }

        return {
            "recommendation": "REVIEW",
            "message": (
                "Review the approved troubleshooting knowledge "
                "before attempting the scenario again."
            ),
            "next_step": "REVIEW_KNOWLEDGE_AND_RETRY",
            "areas_to_improve": feedback,
        }