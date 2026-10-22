from app.services.scenario_engine import WifiScenarioEngine
from app.services.progress_tracker import ProgressTracker


# Start a new training scenario.
engine = WifiScenarioEngine("WIFI-001")

# Create a tracker for the same scenario.
tracker = ProgressTracker(engine.state.scenario_id)


# Simulate the learner checking Wi-Fi status.
action = "check_wifi_status"

action_result = engine.execute_action(action)

if action_result["allowed"]:
    rule_result = engine.evaluate_finding(action)
    record = tracker.record_action(
        action,
        action_result,
        rule_result,
    )

    print("Action executed:")
    print(action_result)

    print("\nBusiness rule evaluation:")
    print(rule_result)

    print("\nRecorded learner evidence:")
    print(record)


# Simulate the learner checking airplane mode.
action = "check_airplane_mode"

action_result = engine.execute_action(action)

if action_result["allowed"]:
    rule_result = engine.evaluate_finding(action)
    record = tracker.record_action(
        action,
        action_result,
        rule_result,
    )

    print("\nSecond action executed:")
    print(action_result)

    print("\nSecond evidence record:")
    print(record)


# Display the complete training history.
print("\nComplete learner action history:")

for record in tracker.get_action_history():
    print(record)

print("\nTotal recorded actions:", len(tracker.get_action_history()))