import asyncio
import logging
from livekit.agents import JobContext, WorkerOptions, cli, voice, AutoSubscribe
from agent.voice_pipeline import get_stt, get_llm, get_tts, get_vad

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stt-debug")

async def entrypoint(ctx: JobContext):
    logger.info(f"Connecting to room: {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    agent = voice.Agent(
        stt=get_stt(),
        llm=get_llm(),
        tts=get_tts(),
        vad=get_vad(),
        instructions="You are a helpful assistant.",
    )

    # Manual event listening if Agent supports it, or just use AgentTask
    # Since we aren't sure about Agent.on, we'll just use a simple session
    session = voice.AgentSession()
    
    await session.start(agent, room=ctx.room)
    logger.info("Session started. Waiting for speech...")

    # We will let it run and watch the logs of the STT plugin itself if it has any,
    # or add a task to watch the transcriptions if we can find where they go.
    
    await asyncio.sleep(60)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
