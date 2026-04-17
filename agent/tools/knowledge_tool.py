"""
knowledge_tool.py - LLM-callable tool for querying the local vector store.
"""
from typing import Annotated
from livekit.agents import function_tool
import logging

from agent.knowledge.store import knowledge_store

logger = logging.getLogger("knowledge-tool")

@function_tool(
    name="search_knowledge_base",
    description="Search the clinic's knowledge base for answers to questions about services, policies, preparation, hours, pricing, etc. Always call this BEFORE answering a factual question about the clinic.",
)
async def search_knowledge_base(
    query: Annotated[str, "The user's question, phrased clearly as a search term."],
) -> str:
    logger.info(f"LLM querying knowledge base for: {query}")
    result = await knowledge_store.search(query, top_k=3)
    return "Here is information from the knowledge base (summarize this concisely and warmly to the caller):\n\n" + result
