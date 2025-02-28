from .vector import main
import asyncio
from dataclasses import dataclass
from llama_index.core import VectorStoreIndex
from pydantic_ai import RunContext
import os
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class Dependencies:
    """Container for system dependencies"""

    index: VectorStoreIndex


SYSTEM_PROMPT = "Your system prompt here."



def initialize_agent() -> Agent[Dependencies, str]:
    """Create and configure the AI agent using PydanticAI and LlamaIndex."""
    model = GeminiModel(model_name="gemini-1.5-flash", api_key="AIzaSyAfHtJ0j3Jqplgcf3u5Duf-hMar8Ig-Yao")

    agent = Agent(
        model=model,
        deps_type=Dependencies,
        system_prompt=SYSTEM_PROMPT,
    )

    return agent

agent = initialize_agent()

@agent.tool
async def retrieve(context: RunContext[Dependencies], query: str) -> str:
    
    index = context.deps.index
    retriever = index.as_retriever()
    nodes = retriever.retrieve(query)
    return f"LlamaIndex Results:\n{nodes}"

async def run_rag_agent(query: str, force_rebuild: bool = False) -> str:
    """Execute RAG pipeline for a given query"""
    index = main()
    deps = Dependencies(index=index)

    response = await agent.run(query, deps=deps)
    return response.data


async def run_rag_agent_example():
    """Example usage"""
    result = await run_rag_agent("what can you tell me from the retrieved information ")
    print(result)


if __name__ == "__main__":
    asyncio.run(run_rag_agent_example())
