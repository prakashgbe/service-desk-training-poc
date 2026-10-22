from dataclasses import dataclass, field

SCENARIO_CONFIGS = {
    "WIFI-001": {
        "scenario_name": "Wi-Fi Disabled",
        "wifi_enabled": False,
        "airplane_mode_enabled": False,
        "corporate_ssid_visible": True,
        "other_employees_affected": False,
        "authentication_error": False,
        "ip_configuration_valid": True,
    },
    "WIFI-002": {
        "scenario_name": "Authentication Failure",
        "wifi_enabled": True,
        "airplane_mode_enabled": False,
        "corporate_ssid_visible": True,
        "other_employees_affected": False,
        "authentication_error": True,
        "ip_configuration_valid": True,
    },
    "WIFI-003": {
        "scenario_name": "Widespread Incident",
        "wifi_enabled": True,
        "airplane_mode_enabled": False,
        "corporate_ssid_visible": True,
        "other_employees_affected": True,
        "authentication_error": False,
        "ip_configuration_valid": True,
    },
}

@dataclass
class WifiScenarioState:
    """
    Represents the simulated state of an employee's Wi-Fi issue.
    """

    scenario_id: str = "WIFI-001"
    scenario_name: str = "Wi-Fi Disabled"

    wifi_enabled: bool = False
    airplane_mode_enabled: bool = False
    corporate_ssid_visible: bool = True

    other_employees_affected: bool = False
    authentication_error: bool = False
    ip_configuration_valid: bool = True

    completed_actions: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

class WifiScenarioEngine:
    """
    Controls the rules and state of the Wi-Fi troubleshooting simulation.
    """

    ALLOWED_ACTIONS = {
        "check_wifi_status",
        "check_airplane_mode",
        "check_corporate_network",
        "check_incident_scope",
        "check_authentication",
        "check_ip_configuration",
        "enable_wifi",
    }

    def __init__(self, scenario_id: str = "WIFI-001"):
        config = SCENARIO_CONFIGS.get(scenario_id)

        if config is None:
            raise ValueError(
                f"Unknown scenario ID: {scenario_id}"
            )

        self.state = WifiScenarioState(
            scenario_id=scenario_id,
            **config,
        )

    def validate_action(self, action: str) -> dict:
        """
        Check whether the requested action is supported.
        """

        if action not in self.ALLOWED_ACTIONS:
            return {
                "allowed": False,
                "message": (
                    f"Action '{action}' is not permitted "
                    "in this simulation."
                ),
            }

        return {
            "allowed": True,
            "message": f"Action '{action}' is permitted.",
        }

    def execute_action(self, action: str) -> dict:
        """
        Execute a permitted troubleshooting action
        and return the simulated result.
        """

        validation = self.validate_action(action)

        if not validation["allowed"]:
            return validation

        state = self.state

        results = {
            "check_wifi_status": {
                "finding": f"Wi-Fi enabled: {state.wifi_enabled}",
                "success": state.wifi_enabled,
            },
            "check_airplane_mode": {
                "finding": (
                    f"Airplane mode enabled: "
                    f"{state.airplane_mode_enabled}"
                ),
                "success": not state.airplane_mode_enabled,
            },
            "check_corporate_network": {
                "finding": (
                    f"Corporate network visible: "
                    f"{state.corporate_ssid_visible}"
                ),
                "success": state.corporate_ssid_visible,
            },
            "check_incident_scope": {
                "finding": (
                    "Other employees affected: "
                    f"{state.other_employees_affected}"
                ),
                "success": True,
            },
            "check_authentication": {
                "finding": (
                    f"Authentication error detected: "
                    f"{state.authentication_error}"
                ),
                "success": not state.authentication_error,
            },
            "check_ip_configuration": {
                "finding": (
                    f"IP configuration valid: "
                    f"{state.ip_configuration_valid}"
                ),
                "success": state.ip_configuration_valid,
            },
        }

        if action == "enable_wifi":
            state.wifi_enabled = True

            result = {
                "finding": "Wi-Fi has been enabled in the simulation.",
                "success": True,
            }
        else:
            result = results[action]

        if action != "enable_wifi":
            result = results[action]

        state.completed_actions.append(action)
        state.findings.append(result["finding"])

        return {
            "allowed": True,
            "action": action,
            **result,
        }

    def evaluate_finding(self, action: str) -> dict:
        """
        Evaluate a troubleshooting finding and determine
        its operational significance and recommended next step.
        """

        state = self.state

        if action == "enable_wifi" and state.wifi_enabled:
            return {
                "finding_type": "remediation_performed",
                "priority": "informational",
                "recommendation": (
                    "Verify Wi-Fi status and continue with the "
                    "approved connectivity verification procedure."
                ),
            }        

        if (
            action == "check_incident_scope"
            and state.other_employees_affected
        ):
            return {
                "finding_type": "potential_widespread_incident",
                "priority": "high",
                "recommendation": (
                    "Follow the approved incident escalation "
                    "procedure. Record the affected location "
                    "and number of employees. Do not declare "
                    "a confirmed outage without sufficient evidence."
                ),
            }

        if (
            action == "check_authentication"
            and state.authentication_error
        ):
            return {
                "finding_type": "authentication_issue",
                "priority": "medium",
                "recommendation": (
                    "Record the authentication error and follow "
                    "the approved authentication troubleshooting "
                    "procedure. Never request the employee's password "
                    "or bypass security controls."
                ),
            }

        if action == "check_wifi_status" and not state.wifi_enabled:
            return {
                "finding_type": "local_connectivity_issue",
                "priority": "low",
                "recommendation": (
                    "Guide the learner to follow the approved "
                    "procedure for enabling Wi-Fi, if permitted, "
                    "and then verify connectivity."
                ),
            }

        return {
            "finding_type": "no_issue_detected_by_this_check",
            "priority": "informational",
            "recommendation": (
                "Continue with the next appropriate troubleshooting "
                "step according to the approved procedure."
            ),
        }