from app.services.progress_tracker import ProgressTracker


tracker = ProgressTracker("WIFI-001")

action_result_1 = {
    "allowed": True,
    "action": "check_wifi_status",
    "finding": "Wi-Fi enabled: False",
    "success": False,
}

rule_result_1 = {
    "finding_type": "local_connectivity_issue",
    "priority": "low",
    "recommendation": "Follow the approved Wi-Fi troubleshooting procedure.",
}

action_result_2 = {
    "allowed": True,
    "action": "check_airplane_mode",
    "finding": "Airplane mode enabled: False",
    "success": True,
}

rule_result_2 = {
    "finding_type": "no_issue_detected_by_this_check",
    "priority": "informational",
    "recommendation": "Continue with the next appropriate troubleshooting step.",
}

record_1 = tracker.record_action(
    "check_wifi_status",
    action_result_1,
    rule_result_1,
)

record_2 = tracker.record_action(
    "check_airplane_mode",
    action_result_2,
    rule_result_2,
)

print("First action record:")
print(record_1)

print("\nSecond action record:")
print(record_2)

print("\nComplete action history:")
for record in tracker.get_action_history():
    print(record)

print("\nTotal recorded actions:", len(tracker.get_action_history()))