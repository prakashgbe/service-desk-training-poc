from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from google.adk.runners import Runner
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.knowledge_agent import knowledge_agent

from app.services.training_session import TrainingSession

from uuid import uuid4

from app.agents.training_simulation_agent import (
    training_simulation_agent,
)

from app.services.assessment_service import AssessmentService

from app.services.learning_journey import LearningJourneyService

app = FastAPI(
    title="Service Desk Training POC",
    description="AI-assisted training for Service Desk engineers",
    version="0.1.0",
)

BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")

class KnowledgeRequest(BaseModel):
    question: str = Field(
        min_length=3,
        max_length=2000,
        description="The learner's troubleshooting question",
    )


class KnowledgeResponse(BaseModel):
    answer: str


class CreateTrainingSessionRequest(BaseModel):
    scenario_id: str = Field(
        default="WIFI-001",
        description="The ID of the training scenario",
    )


class CreateTrainingSessionResponse(BaseModel):
    session_id: str
    scenario_id: str
    scenario_name: str


class TrainingActionRequest(BaseModel):
    action: str = Field(
        min_length=1,
        max_length=100,
        description="The troubleshooting action to execute",
    )


class TrainingActionResponse(BaseModel):
    scenario_id: str
    action_result: dict
    business_rule_result: dict | None
    evidence: dict | None


class TrainingChatRequest(BaseModel):
    session_id: str
    message: str = Field(
        min_length=1,
        max_length=2000,
        description="The learner's natural-language message",
    )


class HintConversationMessage(BaseModel):
    role: str = Field(pattern="^(employee|learner)$")
    text: str = Field(min_length=1, max_length=2000)


class TrainingHintRequest(BaseModel):
    session_id: str
    employee_message: str = Field(min_length=1, max_length=2000)
    conversation: list[HintConversationMessage] = Field(default_factory=list, max_length=40)

session_service = InMemorySessionService()

runner = Runner(
    agent=knowledge_agent,
    app_name="service_desk_training",
    session_service=session_service,
)

training_agent_session_service = InMemorySessionService()

assessment_service = AssessmentService()

learning_journey_service = LearningJourneyService()

training_agent_runner = Runner(
    agent=training_simulation_agent,
    app_name="training_simulation",
    session_service=training_agent_session_service,
)

# The hint role is separate from the employee conversation. It has no tools,
# so requesting a hint cannot execute a troubleshooting action.
hint_agent = Agent(
    name="training_hint_agent",
    model="gemini-3.5-flash-lite",
    description="Provides optional, contextual hints to a Service Desk training learner.",
    instruction="""
You are the optional Hint Coach in a Service Desk training simulation.
The learner is acting as a Service Desk engineer. The employee is the person
reporting the issue. Give one concise, contextual hint to help the learner decide
what to ask or do next. Do not answer as the employee. Do not execute actions.
Do not reveal the complete solution or list every troubleshooting step. Base hints
on the current employee message and conversation. Follow safe enterprise practice:
never ask for passwords, bypass security controls, or suggest unauthorized changes.
If relevant, encourage the learner to follow the approved SOP and verify results.
Return only the hint text, without a heading or markdown list.
""",
)
hint_session_service = InMemorySessionService()
hint_runner = Runner(
    agent=hint_agent,
    app_name="service_desk_training_hints",
    session_service=hint_session_service,
)

# In-memory registry for active training sessions.
training_sessions: dict[str, TrainingSession] = {}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "Service Desk Training POC",
    }

@app.post(
    "/training/sessions",
    response_model=CreateTrainingSessionResponse,
)
def create_training_session(
    request: CreateTrainingSessionRequest,
):
    try:
        training_session = TrainingSession(request.scenario_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    session_id = str(uuid4())

    training_sessions[session_id] = training_session

    return CreateTrainingSessionResponse(
        session_id=session_id,
        scenario_id=training_session.engine.state.scenario_id,
        scenario_name=training_session.engine.state.scenario_name,
    )


@app.post(
    "/training/sessions/{session_id}/actions",
    response_model=TrainingActionResponse,
)
def execute_training_action(
    session_id: str,
    request: TrainingActionRequest,
):
    training_session = training_sessions.get(session_id)

    if training_session is None:
        raise HTTPException(
            status_code=404,
            detail="Training session not found.",
        )

    return training_session.perform_action(request.action)


@app.get("/training/sessions/{session_id}/progress")
def get_training_progress(session_id: str):
    training_session = training_sessions.get(session_id)

    if training_session is None:
        raise HTTPException(
            status_code=404,
            detail="Training session not found.",
        )

    return {
        "session_id": session_id,
        "scenario_id": training_session.engine.state.scenario_id,
        "scenario_name": training_session.engine.state.scenario_name,
        "total_actions": len(training_session.get_progress()),
        "actions": training_session.get_progress(),
    }


@app.post("/knowledge/ask", response_model=KnowledgeResponse)
async def ask_knowledge_agent(request: KnowledgeRequest):
    user_id = "poc_learner"
    session_id = "session_001"

    try:
        await session_service.create_session(
            app_name="service_desk_training",
            user_id=user_id,
            session_id=session_id,
        )

        message = types.Content(
            role="user",
            parts=[types.Part(text=request.question)],
        )

        answer = ""

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        answer += part.text

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="The Knowledge Agent did not return an answer.",
            )

        return KnowledgeResponse(answer=answer)

    except HTTPException:
        raise

    except Exception as exc:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Failed to process the knowledge request.",
        ) from exc


@app.post("/training/chat")
async def training_chat(request: TrainingChatRequest):
    training_session = training_sessions.get(request.session_id)

    if training_session is None:
        raise HTTPException(
            status_code=404,
            detail="Training session not found.",
        )

    user_id = request.session_id
    agent_session_id = request.session_id

    try:
        existing_session = await training_agent_session_service.get_session(
            app_name="training_simulation",
            user_id=user_id,
            session_id=agent_session_id,
        )

        if existing_session is None:
            await training_agent_session_service.create_session(
                app_name="training_simulation",
                user_id=user_id,
                session_id=agent_session_id,
            )

        message = types.Content(
            role="user",
            parts=[
                types.Part(
                    text=(
                        f"Training session ID: {request.session_id}\n"
                        f"Learner message: {request.message}"
                    )
                )
            ],
        )

        answer = ""

        async for event in training_agent_runner.run_async(
            user_id=user_id,
            session_id=agent_session_id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        answer += part.text

        if not answer:
            raise HTTPException(
                status_code=502,
                detail="The Training Simulation Agent returned no answer.",
            )

        return {
            "session_id": request.session_id,
            "answer": answer,
        }

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Failed to process the training conversation."
        )


@app.post("/training/hint")
async def get_training_hint(request: TrainingHintRequest):
    """Return an optional hint without modifying the simulated scenario."""
    if request.session_id not in training_sessions:
        raise HTTPException(status_code=404, detail="Training session not found.")

    hint_session_id = str(uuid4())
    hint_user_id = request.session_id
    conversation_text = "\n".join(
        f"{item.role.title()}: {item.text}" for item in request.conversation[-20:]
    )
    prompt = (
        "Provide one contextual hint for the learner.\n\n"
        f"Current employee message: {request.employee_message}\n\n"
        f"Recent conversation:\n{conversation_text or '(No prior conversation)'}\n\n"
        "Give one concise nudge toward the next appropriate question or approved check, not the full answer. Never speak as the employee, never claim a check has been performed, and never execute a tool."
    )

    try:
        await hint_session_service.create_session(
            app_name="service_desk_training_hints",
            user_id=hint_user_id,
            session_id=hint_session_id,
        )
        message = types.Content(role="user", parts=[types.Part(text=prompt)])
        hint_text = ""
        async for event in hint_runner.run_async(
            user_id=hint_user_id,
            session_id=hint_session_id,
            new_message=message,
        ):
            if event.is_final_response() and event.content:
                for part in event.content.parts:
                    if part.text:
                        hint_text += part.text

        if not hint_text.strip():
            raise HTTPException(status_code=502, detail="The Hint Coach returned no hint.")
        return {"session_id": request.session_id, "hint": hint_text.strip()}
    except HTTPException:
        raise
    except Exception as exc:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Failed to generate a training hint.",
        ) from exc

@app.get("/training/sessions/{session_id}/assessment")
def get_training_assessment(session_id: str):
    training_session = training_sessions.get(session_id)

    if training_session is None:
        raise HTTPException(
            status_code=404,
            detail="Training session not found."
        )

    assessment = assessment_service.assess(
        training_session.get_progress()
    )

    return {
        "session_id": session_id,
        "scenario_id": training_session.engine.state.scenario_id,
        "assessment": assessment,
    }

@app.get("/training/sessions/{session_id}/learning-journey")
def get_learning_journey(session_id: str):
    training_session = training_sessions.get(session_id)

    if training_session is None:
        raise HTTPException(
            status_code=404,
            detail="Training session not found."
        )

    assessment = assessment_service.assess(
        training_session.get_progress()
    )

    recommendation = learning_journey_service.recommend_next_step(
        assessment
    )

    return {
        "session_id": session_id,
        "scenario_id": training_session.engine.state.scenario_id,
        "assessment": assessment,
        "learning_journey": recommendation,
    }