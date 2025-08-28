"""
QA Engine Module
Handles question answering using RAG (Retrieval-Augmented Generation)
"""

import logging
from typing import List, Dict, Any
import threading
import streamlit as st

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

# Callback base import (works for both LC 0.1 and 0.2+)
try:
    from langchain_core.callbacks import BaseCallbackHandler  # LC 0.2+
except ImportError:
    from langchain.callbacks.base import BaseCallbackHandler  # LC 0.1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== STOP FLAG (for stopping generation mid-way) =====
stop_flag = threading.Event()

def stop_generation():
    """Trigger stop signal for ongoing response generation."""
    stop_flag.set()

def reset_stop():
    """Reset stop signal before a new response."""
    stop_flag.clear()


class _StreamingStopHandler(BaseCallbackHandler):
    """
    Streams tokens to a collector and interrupts when stop_flag is set.
    """

    def __init__(self, on_token):
        self.on_token = on_token

    # LangChain calls this on each token during streaming
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        if stop_flag.is_set():
            # Raising here cleanly cancels the LLM call/chain
            raise KeyboardInterrupt("Stopped by user")
        self.on_token(token)


class QAEngine:
    """
    Handles question answering using RAG with Google Gemini models
    """

    def __init__(self, vector_store, model_name: str = "gemini-2.5-pro", temperature: float = 0.7):
        self.vector_store = vector_store
        self.model_name = model_name
        self.temperature = temperature
        self.llm = None
        self.qa_chain = None

        # Initialize the language model
        try:
            # Some versions require streaming=True for token callbacks; others ignore it.
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=temperature,
                    max_output_tokens=1000,
                    streaming=True  # If unsupported, the outer except will retry without it.
                )
            except TypeError:
                self.llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=temperature,
                    max_output_tokens=1000
                )
            logger.info(f"Initialized ChatGoogleGenerativeAI with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGoogleGenerativeAI: {str(e)}")
            st.error("Failed to initialize language model. Please check your Google API key.")

        # Create custom prompt template & QA chain
        self.prompt_template = self._create_prompt_template()
        self._initialize_qa_chain()

    def _create_prompt_template(self) -> PromptTemplate:
        template = """
You are a helpful AI assistant that answers questions based on the provided document context. 
Use the following pieces of context to answer the question at the end.

Context:
{context}

Question: {question}

Instructions:
1. Answer the question based ONLY on the provided context
2. If the answer cannot be found in the context, say "I cannot find that information in the provided document"
3. Be concise but comprehensive in your response
4. If relevant, quote specific parts of the document
5. Maintain a helpful and professional tone

Answer:"""
        return PromptTemplate(template=template, input_variables=["context", "question"])

    def _initialize_qa_chain(self):
        if not self.vector_store or not self.llm:
            logger.error("Cannot initialize QA chain: vector store or LLM not available")
            return

        try:
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )

            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever,
                return_source_documents=True,
                chain_type_kwargs={"prompt": self.prompt_template}
            )
            logger.info("QA chain initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing QA chain: {str(e)}")
            st.error(f"Failed to initialize QA system: {str(e)}")

    def answer_question(self, question: str) -> str:
        """
        Answer a question using the QA chain, with streaming + stoppable generation.
        """
        if not self.qa_chain:
            return "QA system is not properly initialized. Please check your configuration."
        if not question.strip():
            return "Please provide a valid question."

        try:
            logger.info(f"Processing question: {question}")
            reset_stop()

            # Collect streamed answer
            answer_parts: List[str] = []
            handler = _StreamingStopHandler(on_token=lambda t: answer_parts.append(t))

            # Invoke the chain; tokens will arrive via handler
            response = self.qa_chain({"query": question}, callbacks=[handler])

            # Prefer the streamed tokens; fall back to `result` if no tokens were streamed.
            answer = "".join(answer_parts).strip()
            if not answer:
                answer = response.get("result", "⚠️ I couldn't generate an answer.")
            return answer

        except KeyboardInterrupt:
            logger.warning("Generation stopped by user")
            return "⚠️ Chat stopped by user."
        except Exception as e:
            logger.error(f"Error answering question: {str(e)}")
            return f"I encountered an error while processing your question: {str(e)}"

    def answer_with_sources(self, question: str) -> Dict[str, Any]:
        """
        Answer a question and return both answer and source documents.
        """
        if not self.qa_chain:
            return {"answer": "QA system is not properly initialized.", "sources": [], "confidence": 0.0}

        try:
            reset_stop()
            response = self.qa_chain({"query": question})
            answer = response.get("result", "⚠️ No answer generated.")
            source_docs = response.get("source_documents", [])

            sources = []
            for i, doc in enumerate(source_docs):
                txt = doc.page_content
                sources.append({
                    "content": (txt[:200] + "...") if len(txt) > 200 else txt,
                    "metadata": doc.metadata,
                    "chunk_id": i
                })

            confidence = min(1.0, len(sources) / 4.0)
            return {"answer": answer, "sources": sources, "confidence": confidence}
        except Exception as e:
            logger.error(f"Error answering with sources: {str(e)}")
            return {"answer": f"Error: {str(e)}", "sources": [], "confidence": 0.0}

    def get_document_summary(self, max_length: int = 500) -> str:
        try:
            summary_question = (
                "Please provide a comprehensive summary of this document, including "
                "its main topics, key points, and overall purpose."
            )
            response = self.answer_question(summary_question)
            return (response[:max_length] + "...") if len(response) > max_length else response
        except Exception as e:
            logger.error(f"Error generating document summary: {str(e)}")
            return "Unable to generate document summary."

    def suggest_questions(self) -> List[str]:
        try:
            sample_docs = self.vector_store.similarity_search("main topics key points", k=3)
            if not sample_docs:
                return []

            suggestion_prompt = """
            Based on the following document content, suggest 5 relevant questions that a user might ask:

            Content:
            {content}

            Questions should be:
            1. Specific to the document content
            2. Useful for understanding key information
            3. Varied in scope (some detailed, some general)

            Format your response as a numbered list.
            """

            content = "\n".join([doc.page_content[:300] for doc in sample_docs])
            if self.llm:
                response = self.llm.predict(suggestion_prompt.format(content=content))
                questions = []
                for line in response.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    # Strip "1. " / "- " prefixes
                    if line[0].isdigit() and "." in line:
                        line = line.split(".", 1)[-1].strip()
                    elif line.startswith("-"):
                        line = line[1:].strip()
                    if "?" in line:
                        questions.append(line)
                return questions[:5]
            return []
        except Exception as e:
            logger.error(f"Error generating question suggestions: {str(e)}")
            return []

    def update_model_parameters(self, temperature: float = None, max_tokens: int = None):
        try:
            if temperature is not None:
                self.temperature = temperature
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_output_tokens=max_tokens or 1000,
                    streaming=True
                )
            except TypeError:
                self.llm = ChatGoogleGenerativeAI(
                    model=self.model_name,
                    temperature=self.temperature,
                    max_output_tokens=max_tokens or 1000
                )
            self._initialize_qa_chain()
            logger.info(f"Updated model parameters: temperature={self.temperature}")
        except Exception as e:
            logger.error(f"Error updating model parameters: {str(e)}")

    def get_system_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "vector_store_initialized": self.vector_store is not None,
            "qa_chain_initialized": self.qa_chain is not None,
            "llm_initialized": self.llm is not None
        }
