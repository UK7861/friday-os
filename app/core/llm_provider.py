import os
from dotenv import load_dotenv

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except ImportError:
    ChatGoogleGenerativeAI = None

try:
    from langchain_ollama import ChatOllama
except ImportError:
    try:
        from langchain_community.chat_models import ChatOllama
    except ImportError:
        ChatOllama = None

load_dotenv()

class LLMFactory:
    @staticmethod
    def get_llm(provider: str = "openai", model: str = None):
        if provider == "openai":
            if ChatOpenAI is None:
                raise ImportError("langchain-openai not installed")
            return ChatOpenAI(
                model=model or "gpt-4-turbo-preview",
                api_key=os.getenv("OPENAI_API_KEY")
            )
        elif provider == "google":
            if ChatGoogleGenerativeAI is None:
                raise ImportError("langchain-google-genai not installed")
            return ChatGoogleGenerativeAI(
                model=model or "gemini-pro",
                google_api_key=os.getenv("GEMINI_API_KEY")
            )
        elif provider == "ollama":
            if ChatOllama is None:
                raise ImportError("langchain-ollama not installed")
            return ChatOllama(
                model=model or "llama3",
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")

llm_manager = LLMFactory()
