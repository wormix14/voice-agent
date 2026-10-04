import asyncio
import logging
import json
from dotenv import load_dotenv
from db.session import engine
from db.models import Base
from livekit import agents
from livekit.agents import (
    AgentServer,
    AgentSession,
    Agent,
    inference,
    room_io,
    TurnHandlingOptions,
    InterruptionOptions,
    EndpointingOptions,
    PreemptiveGenerationOptions,
    JobContext
)
from livekit.agents.beta.tools import EndCallTool
from livekit.plugins import ai_coustics, deepgram, cartesia, openai
from tools import process_and_save
 
load_dotenv(".env.local")
 
logger = logging.getLogger(__name__)
 
 
class Assistant(Agent):
    def __init__(self, topic: str ) -> None:
        super().__init__(
            instructions=f"""
        You are a professional intake assistant.
        Your goal is to conduct an interview strictly on the topic: "{topic}".
        Always speak the language of the user.
        Say numbers, dates etc only in language that user is speaking.
        RULES:
        - Stay focused solely on "{topic}".
        - Ask clear, short questions (1-2 sentences at a time).
        - Gently decline answering off-topic questions and bring the user back to "{topic}".
        - Once you collect all relevant information about "{topic}", summarize what was said and wrap up.
        """,
            tools=[
                EndCallTool(
                    extra_description="Call after the patient has answered the final question about anything urgent.",
                    end_instructions="Briefly say goodbye to the patient in their language.",
                    delete_room=True,
                )
            ],
        )
 
 
server = AgentServer()
 
 
@server.on("worker_started")
def init_db(*args, **kwargs):
    Base.metadata.create_all(bind=engine)
 
 
@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):
    try:
        metadata = json.loads(ctx.job.metadata)
        topic = metadata['topic']
    except (json.JSONDecodeError, TypeError):
        topic = ctx.job.metadata

    session = AgentSession(
        stt=deepgram.STT(model="nova-3-general", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=cartesia.TTS(
            model="sonic-3.6",
            voice="47c38ca4-5f35-497b-b1a3-415245fb35e1",
            language="de"
        ),
        turn_handling=TurnHandlingOptions(
            turn_detection=inference.TurnDetector(),
            preemptive_generation=PreemptiveGenerationOptions(enabled=False),
            endpointing=EndpointingOptions(min_delay=0.2, max_delay=0.8),
            interruption=InterruptionOptions(
                enabled=True,
                mode="adaptive",
                min_duration=0.3,
            ),
        ),
    )
 

    async def write_transcript():
        try:
            await asyncio.to_thread(
                process_and_save, session.history, topic)

        except Exception:
            logger.exception("failed to save transcript")
 
    ctx.add_shutdown_callback(write_transcript)
 
    @session.on("close")
    def on_session_close(ev):
        ctx.shutdown(reason="session closed")
 
    await session.start(
        room=ctx.room,
        agent=Assistant(topic=topic),
        room_options=room_io.RoomOptions(
            delete_room_on_close=True,
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=ai_coustics.audio_enhancement(
                    model=ai_coustics.EnhancerModel.QUAIL_VF_S
                ),
            ),
        ),
    )

    await ctx.wait_for_participant()
    
    await session.generate_reply(
        instructions="Greet the user and offer your assistance."
    )
 
 
if __name__ == "__main__":
    agents.cli.run_app(server)