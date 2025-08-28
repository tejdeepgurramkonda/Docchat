"""
QA Engine Module
Handles question answering using RAG (Retrieval-Augmented Generation)
"""

import logging
from typing import List, Dict, Any
import threading

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
            # Note: This is handled at FastAPI level, not Streamlit
            raise e

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
            # Note: This is handled at FastAPI level, not Streamlit
            raise e

    def answer_question(self, question: str, max_retries: int = 2) -> str:
        """
        Answer a question using the QA chain, with streaming + stoppable generation.
        Includes retry logic for temporary API failures.
        """
        if not self.qa_chain:
            return "QA system is not properly initialized. Please check your configuration."
        if not question.strip():
            return "Please provide a valid question."

        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Processing question (attempt {attempt + 1}): {question}")
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
                error_str = str(e)
                logger.error(f"Error answering question (attempt {attempt + 1}): {error_str}")
                
                # Check if this is a retryable error
                is_retryable = (
                    "500" in error_str or 
                    "502" in error_str or 
                    "503" in error_str or
                    "temporarily unavailable" in error_str.lower() or
                    "service unavailable" in error_str.lower() or
                    "timeout" in error_str.lower()
                )
                
                # If this is the last attempt or error is not retryable, return error message
                if attempt == max_retries or not is_retryable:
                    # Handle specific Google API errors
                    if "500 An internal error has occurred" in error_str:
                        return "🔧 Google AI service is temporarily unavailable. This could be due to:\n" \
                               "• API quota limits reached\n" \
                               "• Temporary service outage\n" \
                               "• High request volume\n\n" \
                               "Please try again in a few minutes. If the issue persists, check your API quota at: " \
                               "https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas"
                    elif "400" in error_str or "invalid" in error_str.lower():
                        return "❌ Invalid request to Google AI service. Please check:\n" \
                               "• Your API key is valid\n" \
                               "• The request format is correct\n" \
                               "• Try rephrasing your question"
                    elif "401" in error_str or "unauthorized" in error_str.lower():
                        return "🔑 Authentication failed with Google AI. Please verify:\n" \
                               "• Your API key is correct\n" \
                               "• The API key has the necessary permissions\n" \
                               "• The API is enabled in your Google Cloud project"
                    elif "429" in error_str or "quota" in error_str.lower():
                        return "⏱️ Rate limit exceeded. Please:\n" \
                               "• Wait a few minutes before trying again\n" \
                               "• Check your API quota limits\n" \
                               "• Consider upgrading your API plan if needed"
                    else:
                        return f"❌ I encountered an error while processing your question:\n{error_str}\n\n" \
                               "💡 Troubleshooting tips:\n" \
                               "• Check your internet connection\n" \
                               "• Verify your Google API key is valid\n" \
                               "• Try asking a simpler question\n" \
                               "• Report persistent issues at: https://developers.generativeai.google/guide/troubleshooting"
                else:
                    # Wait a bit before retrying
                    import time
                    wait_time = (attempt + 1) * 2  # 2, 4, 6 seconds
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    continue
        
        # This should never be reached, but just in case
        return "❌ Failed to process question after multiple attempts."

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
    
    def validate_api_connection(self) -> Dict[str, Any]:
        """
        Validate Google API connection and return status
        """
        import os
        
        validation_result = {
            "api_key_present": bool(os.getenv("GOOGLE_API_KEY")),
            "llm_initialized": self.llm is not None,
            "connection_test": "not_tested",
            "error": None
        }
        
        # Test basic API connection with a simple query
        if validation_result["api_key_present"] and validation_result["llm_initialized"]:
            try:
                # Simple test query
                test_response = self.llm.invoke("Say 'API connection successful'")
                if test_response and test_response.content:
                    validation_result["connection_test"] = "successful"
                    validation_result["test_response"] = test_response.content[:50]
                else:
                    validation_result["connection_test"] = "failed"
                    validation_result["error"] = "Empty response from API"
            except Exception as e:
                validation_result["connection_test"] = "failed"
                validation_result["error"] = str(e)
        else:
            validation_result["connection_test"] = "skipped"
            if not validation_result["api_key_present"]:
                validation_result["error"] = "GOOGLE_API_KEY not set"
            elif not validation_result["llm_initialized"]:
                validation_result["error"] = "LLM not initialized"
        
        return validation_result
