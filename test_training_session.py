from app.services.training_session import TrainingSession


# Start a training session.
session = TrainingSession("WIFI-001")

print("Scenario:", session.engine.state.scenario_name)

# Action 1: Check Wi-Fi status.
result_1 = session.perform_action("check_wifi_status")

print("\nAction 1 result:")
print(result_1)

# Action 2: Check airplane mode.
result_2 = session.perform_action("check_airplane_mode")

print("\nAction 2 result:")
print(result_2)

# Action 3: Attempt an unsupported action.
result_3 = session.perform_action("disable_security_controls")

print("\nUnsupported action result:")
print(result_3)

# Display the complete progress history.
print("\nLearner progress:")

for record in session.get_progress():
    print(record)

print("\nTotal recorded actions:", len(session.get_progress()))