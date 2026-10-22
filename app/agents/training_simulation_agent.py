from google.adk.agents import Agent

from app.services.training_session import TrainingSession


def perform_troubleshooting_action(
    action: str,
    session_id: str,
) -> dict:
    """
    Execute a supported troubleshooting action
    within an existing training session.

    Args:
        action: The supported troubleshooting action.
        session_id: The ID of the active training session.
    """

    from app.main import training_sessions

    training_session = training_sessions.get(session_id)

    if training_session is None:
        return {
            "success": False,
            "message": "Training session not found.",
        }

    return training_session.perform_action(action)


training_simulation_agent = Agent(
    name="training_simulation_agent",
    model="gemini-3.5-flash-lite",
    description=(
        "Helps Service Desk learners troubleshoot "
        "simulated IT support scenarios."
    ),
    instruction="""
You are the Training Simulation Agent in a Service Desk training POC.

Your job is to interpret the learner's troubleshooting request
and use the perform_troubleshooting_action tool to execute
the appropriate supported action.

Supported actions:
- check_wifi_status
- check_airplane_mode
- check_corporate_network
- check_incident_scope
- check_authentication
- check_ip_configuration
- enable_wifi

Rules:
1. Use the tool when the learner clearly requests a supported check.
2. Always pass the session ID supplied by the caller.
3. Use only the supported action identifiers.
4. Explain the returned findings and recommendations clearly.
5. Never invent results or claim an action succeeded unless
   the tool confirms it.
6. If the request is ambiguous, ask a clarifying question.
7. Never recommend bypassing security controls or requesting passwords.
8. Explain that the results belong to a simulated training environment.
""",
    tools=[perform_troubleshooting_action],
)