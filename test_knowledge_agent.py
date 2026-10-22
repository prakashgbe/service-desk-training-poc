import asyncio

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agents.knowledge_agent import knowledge_agent


async def main():
    load_dotenv()

    session_service = InMemorySessionService()

    runner = Runner(
        agent=knowledge_agent,
        app_name="service_desk_training",
        session_service=session_service,
    )

    user_id = "learner_001"
    session_id = "session_001"

    await session_service.create_session(
        app_name="service_desk_training",
        user_id=user_id,
        session_id=session_id,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="A laptop cannot connect to corporate Wi-Fi. "
                "What should a junior Service Desk engineer check first?"
            )
        ],
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    print("\nKnowledge Agent response:\n")
                    print(part.text)


if __name__ == "__main__":
    asyncio.run(main())