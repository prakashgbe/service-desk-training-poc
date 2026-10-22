from app.services.scenario_engine import WifiScenarioEngine


engine = WifiScenarioEngine("WIFI-001")

print("Initial Wi-Fi status:")
print(engine.execute_action("check_wifi_status"))

print("\nEnable Wi-Fi:")
print(engine.execute_action("enable_wifi"))

print("\nVerify Wi-Fi status:")
print(engine.execute_action("check_wifi_status"))

print("\nRecorded actions:")
print(engine.state.completed_actions)