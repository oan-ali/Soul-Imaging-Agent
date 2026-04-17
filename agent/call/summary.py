"""
summary.py — Generates a structured call summary using the LLM after the call ends.
"""
from openai import AsyncOpenAI
from agent.config import settings

async def generate_call_summary(transcript: list[dict], caller_data) -> str:
    """Generate a concise, structured summary of the completed call."""
    
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    transcript_text = "\n".join(
        [f"{'Caller' if t.get('role') == 'user' else 'Agent'}: {t.get('content', '')}" for t in transcript]
    )

    prompt = f"""Summarize this phone call in 2-3 sentences. Include:
1. Why the caller called
2. What actions were taken (if any)
3. Any follow-up needed

Caller data collected: {caller_data.model_dump_json() if caller_data else 'None'}

Transcript:
{transcript_text}

Write the summary as a single paragraph, suitable for a call log dashboard."""

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=200,
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
