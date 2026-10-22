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
        "reconnection_succeeds": False,
    },
    "WIFI-002": {
        "scenario_name": "Authentication Failure",
        "wifi_enabled": True,
        "airplane_mode_enabled": False,
        "corporate_ssid_visible": True,
        "other_employees_affected": False,
        "authentication_error": True,
        "ip_configuration_valid": True,
        "reconnection_succeeds": False,
    },
    "WIFI-003": {
        "scenario_name": "Widespread Incident",
        "wifi_enabled": True,
        "airplane_mode_enabled": False,
        "corporate_ssid_visible": True,
        "other_employees_affected": True,
        "authentication_error": False,
        "ip_configuration_valid": True,
        "reconnection_succeeds": False,
    },
}


@dataclass
class WifiScenarioState:
    """Authoritative state for one simulated employee Wi-Fi incident."""

    scenario_id: str = "WIFI-001"
    scenario_name: str = "Wi-Fi Disabled"
    wifi_enabled: bool = False
    airplane_mode_enabled: bool = False
    corporate_ssid_visible: bool = True
    other_employees_affected: bool = False
    authentication_error: bool = False
    ip_configuration_valid: bool = True
    reconnection_succeeds: bool = False
    reconnection_attempted: bool = False
    connectivity_restored: bool = False
    escalation_required: bool = False
    escalation_recorded: bool = False
    completed_actions: list[str] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

    @property
    def incident_status(self) -> str:
        if self.connectivity_restored:
            return "RESOLVED"
        if self.escalation_recorded:
            return "UNRESOLVED_ESCALATED"
        if self.escalation_required:
            return "UNRESOLVED_ESCALATION_REQUIRED"
        return "IN_PROGRESS"


class WifiScenarioEngine:
    """Executes approved actions and owns the authoritative incident state."""

    ALLOWED_ACTIONS = {
        "check_wifi_status",
        "check_airplane_mode",
        "check_corporate_network",
        "check_incident_scope",
        "check_authentication",
        "check_ip_configuration",
        "enable_wifi",
        "attempt_reconnect",
        "verify_connectivity",
        "escalate_incident",
    }

    def __init__(self, scenario_id: str = "WIFI-001"):
        config = SCENARIO_CONFIGS.get(scenario_id)
        if config is None:
            raise ValueError(f"Unknown scenario ID: {scenario_id}")
        self.state = WifiScenarioState(scenario_id=scenario_id, **config)

    def validate_action(self, action: str) -> dict:
        if action not in self.ALLOWED_ACTIONS:
            return {
                "allowed": False,
                "message": f"Action '{action}' is not permitted in this simulation.",
            }
        return {"allowed": True, "message": f"Action '{action}' is permitted."}

    def execute_action(self, action: str) -> dict:
        validation = self.validate_action(action)
        if not validation["allowed"]:
            return validation

        state = self.state
        if action == "enable_wifi":
            state.wifi_enabled = True
            result = {
                "finding": "Wi-Fi has been enabled in the simulation.",
                "success": True,
            }
        elif action == "attempt_reconnect":
            state.reconnection_attempted = True
            if (
                state.wifi_enabled
                and not state.airplane_mode_enabled
                and state.corporate_ssid_visible
                and state.reconnection_succeeds
                and not state.authentication_error
                and state.ip_configuration_valid
            ):
                state.connectivity_restored = True
                state.escalation_required = False
                result = {
                    "finding": "Reconnection attempt succeeded; corporate Wi-Fi connectivity restored.",
                    "success": True,
                }
            else:
                state.connectivity_restored = False
                state.escalation_required = True
                result = {
                    "finding": "Reconnection attempt failed; corporate Wi-Fi connectivity not restored.",
                    "success": False,
                }
        elif action == "verify_connectivity":
            connected = bool(state.connectivity_restored)
            if not connected:
                state.escalation_required = True
            result = {
                "finding": f"Corporate Wi-Fi connectivity verified: {connected}",
                "success": connected,
            }
        elif action == "escalate_incident":
            if state.connectivity_restored:
                result = {
                    "finding": "Escalation not required because connectivity is restored.",
                    "success": False,
                }
            else:
                state.escalation_required = True
                state.escalation_recorded = True
                result = {
                    "finding": "Simulated escalation recorded; incident remains unresolved.",
                    "success": True,
                }
        else:
            results = {
                "check_wifi_status": {
                    "finding": f"Wi-Fi enabled: {state.wifi_enabled}",
                    "success": state.wifi_enabled,
                },
                "check_airplane_mode": {
                    "finding": f"Airplane mode enabled: {state.airplane_mode_enabled}",
                    "success": not state.airplane_mode_enabled,
                },
                "check_corporate_network": {
                    "finding": f"Corporate network visible: {state.corporate_ssid_visible}",
                    "success": state.corporate_ssid_visible,
                },
                "check_incident_scope": {
                    "finding": f"Other employees affected: {state.other_employees_affected}",
                    "success": True,
                },
                "check_authentication": {
                    "finding": f"Authentication error detected: {state.authentication_error}",
                    "success": not state.authentication_error,
                },
                "check_ip_configuration": {
                    "finding": f"IP configuration valid: {state.ip_configuration_valid}",
                    "success": state.ip_configuration_valid,
                },
            }
            result = results[action]

            if action == "check_incident_scope" and state.other_employees_affected:
                state.escalation_required = True
            if action == "check_authentication" and state.authentication_error:
                state.escalation_required = True

        state.completed_actions.append(action)
        state.findings.append(result["finding"])
        return {
            "allowed": True,
            "action": action,
            **result,
            "incident_status": state.incident_status,
        }

    def evaluate_finding(self, action: str) -> dict:
        state = self.state
        if action == "enable_wifi" and state.wifi_enabled:
            return {
                "finding_type": "remediation_performed",
                "priority": "informational",
                "recommendation": (
                    "Verify connectivity; enabling Wi-Fi alone does not prove "
                    "the employee is connected."
                ),
            }
        if action == "attempt_reconnect" and not state.connectivity_restored:
            return {
                "finding_type": "reconnection_failed",
                "priority": "high",
                "recommendation": (
                    "Document the failed attempt, verify connectivity status, "
                    "and follow the approved escalation procedure."
                ),
            }
        if action == "verify_connectivity":
            return {
                "finding_type": (
                    "connectivity_verified"
                    if state.connectivity_restored
                    else "connectivity_not_restored"
                ),
                "priority": "informational" if state.connectivity_restored else "high",
                "recommendation": (
                    "Record successful verification."
                    if state.connectivity_restored
                    else "Do not mark the incident resolved; continue approved checks or escalate."
                ),
            }
        if action == "escalate_incident":
            return {
                "finding_type": (
                    "simulated_escalation_recorded"
                    if state.escalation_recorded
                    else "escalation_not_recorded"
                ),
                "priority": "informational" if state.escalation_recorded else "medium",
                "recommendation": (
                    "The incident remains unresolved; record escalation as simulated."
                    if state.escalation_recorded
                    else "Do not escalate if connectivity has already been verified."
                ),
            }
        if action == "check_incident_scope" and state.other_employees_affected:
            return {
                "finding_type": "potential_widespread_incident",
                "priority": "high",
                "recommendation": (
                    "Follow the approved escalation procedure. Record location and "
                    "number of affected employees; do not declare a confirmed outage "
                    "without sufficient evidence."
                ),
            }
        if action == "check_authentication" and state.authentication_error:
            return {
                "finding_type": "authentication_issue",
                "priority": "medium",
                "recommendation": (
                    "Record the authentication error and follow the approved procedure. "
                    "Never request the employee's password or bypass security controls."
                ),
            }
        if action == "check_wifi_status" and not state.wifi_enabled:
            return {
                "finding_type": "local_connectivity_issue",
                "priority": "low",
                "recommendation": (
                    "Follow the approved procedure for enabling Wi-Fi, if permitted, "
                    "then verify connectivity."
                ),
            }
        return {
            "finding_type": "no_issue_detected_by_this_check",
            "priority": "informational",
            "recommendation": "Continue with the next appropriate approved troubleshooting step.",
        }
