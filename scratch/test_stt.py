import asyncio
import os
from dotenv import load_dotenv
from livekit.plugins import gladia

load_dotenv()

async def test_stt():
    api_key = os.getenv("GLADIA_API_KEY")
    print(f"Testing Gladia STT with API Key: {api_key[:5]}...{api_key[-5:]}")
    
    try:
        stt = gladia.STT(api_key=api_key, languages=["en"])
        print("STT Plugin initialized successfully.")
        
        # Testing authorization by making a dummy request if possible or checking if it raised error on init
        # Most plugins don't check auth until stream starts, but let's see.
        
        print("STT check complete (Initialization only). To verify full functionality, a stream is required.")
        
    except Exception as e:
        print(f"Error initializing STT: {e}")

if __name__ == "__main__":
    asyncio.run(test_stt())
