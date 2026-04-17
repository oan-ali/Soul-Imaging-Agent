import asyncio
import os
from dotenv import load_dotenv
from livekit.plugins import cartesia

load_dotenv()

async def test_tts():
    api_key = os.getenv("CARTESIA_API_KEY")
    voice_id = os.getenv("CARTESIA_VOICE_ID")
    print(f"Testing Cartesia TTS with API Key: {api_key[:8]}... and Voice: {voice_id}")
    
    try:
        tts = cartesia.TTS(api_key=api_key, voice=voice_id)
        print("TTS Plugin initialized successfully.")
        
        # Test generation (this will usually verify the API key)
        # We don't need to play it, just see if it errors
        print("Attempting to synthesize small text...")
        async for part in tts.synthesize("Hello world"):
            print("Received audio part.")
            break
        print("TTS Functional Test: SUCCESS")
        
    except Exception as e:
        print(f"TTS Functional Test: FAILED - {e}")

if __name__ == "__main__":
    asyncio.run(test_tts())
