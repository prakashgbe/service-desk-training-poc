from app.services.training_session import TrainingSession
from app.services.assessment_service import AssessmentService


# Create a fresh Wi-Fi troubleshooting session
session = TrainingSession("WIFI-001")

# Simulate the learner's troubleshooting journey
session.perform_action("check_wifi_status")
session.perform_action("enable_wifi")
session.perform_action("check_wifi_status")

# Assess the learner's actions
action_history = session.get_progress()
assessment = AssessmentService().assess(action_history)

print("\nAssessment Result")
print("-----------------")
print(f"Score: {assessment['score']}/{assessment['maximum_score']}")
print("\nFeedback:")

for item in assessment["feedback"]:
    print(f"- {item}")

print("\nCriteria:")
for criterion, passed in assessment["criteria"].items():
    print(f"- {criterion}: {passed}")