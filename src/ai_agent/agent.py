from dataclasses import dataclass
from llama_index.core import VectorStoreIndex
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from .config import config
from .vector import VectorService
from .database import DatabaseService

@dataclass
class AgentDependencies:
    """Container for agent dependencies"""
    index: VectorStoreIndex
    vector_service: VectorService
    db_service: DatabaseService

class RAGAgent:
    """Retrieval Augmented Generation Agent Service"""
    
    SYSTEM_PROMPT = """You are a helpful AI assistant with access to a knowledge base.
    Your responses should be based on the information retrieved from the knowledge base.
    If you don't find relevant information, please indicate that."""

    def __init__(self):
        self.model = GeminiModel(
            model_name=config.llm_config.model_name,
            api_key=config.llm_config.api_key
        )
        self.agent = self._initialize_agent()
        self.vector_service = VectorService()
        self.db_service = DatabaseService()

    def _initialize_agent(self) -> Agent[AgentDependencies, str]:
        """Initialize the AI agent with dependencies"""
        return Agent(
            model=self.model,
            deps_type=AgentDependencies,
            system_prompt=self.SYSTEM_PROMPT,
        )

    @property
    def retrieve(self):
        """Decorator for the retrieve tool"""
        return self.agent.tool

    @property
    def _retrieve_tool(self):
        """Retrieve relevant information from the vector store"""
        @self.agent.tool
        async def retrieve(context: RunContext[AgentDependencies], query: str) -> str:
            index = context.deps.index
            retriever = index.as_retriever()
            nodes = retriever.retrieve(query)
            return f"Retrieved Information:\n{nodes}"
        return retrieve

    async def process_query(self, query: str, force_rebuild: bool = False) -> str:
        """Process a query using the RAG pipeline"""
        # Initialize or get index
        index = await self.vector_service.get_index(force_rebuild)
        
        # Set up dependencies
        deps = AgentDependencies(
            index=index,
            vector_service=self.vector_service,
            db_service=self.db_service
        )

        # Ensure retrieve tool is initialized
        _ = self._retrieve_tool

        # Run the agent
        response = await self.agent.run(query, deps=deps)
        return response.data

# Create global agent instance
rag_agent = RAGAgent()

async def run_example():
    """Example usage of the RAG agent"""
    result = await rag_agent.process_query(
        "What can you tell me from the retrieved information?"
    )
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_example())


