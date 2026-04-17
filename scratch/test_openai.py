import asyncio
import os
from dotenv import load_dotenv
from livekit.plugins import openai

load_dotenv()

async def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"Testing OpenAI with API Key: {api_key[:10]}...")
    
    try:
        llm = openai.LLM(api_key=api_key)
        print("OpenAI LLM initialized.")
        
        # Test a simple chat
        # Actually LLM doesn't verify on init.
        # Let's try TTS if we want to confirm keys for speech.
        tts = openai.TTS(api_key=api_key)
        print("OpenAI TTS initialized.")
        
        async for part in tts.synthesize("Hello world"):
            print("Received OpenAI audio part.")
            break
        print("OpenAI Functional Test: SUCCESS")
        
    except Exception as e:
        print(f"OpenAI Functional Test: FAILED - {e}")

if __name__ == "__main__":
    asyncio.run(test_openai())
