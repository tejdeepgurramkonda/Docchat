"""
DOCChat - FastAPI Application
A web application where users can upload documents, chat with them, 
manage chat history, stop responses mid-way, and delete chats/documents.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables first
load_dotenv()

# Production settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
PORT = int(os.getenv("PORT", 8000))

# Import utility modules with error handling
try:
    from utils.file_handler import FileHandler
    from utils.chunker import TextChunker
    from utils.embedder import DocumentEmbedder
    from utils.qa_engine import QAEngine, stop_generation, reset_stop
    from database import db
    logger.info("All utility modules imported successfully")
except Exception as e:
    logger.error(f"Error importing utility modules: {e}")
    # Create a minimal FastAPI app for health checks even if imports fail
    pass

# Initialize FastAPI app
app = FastAPI(
    title="DOCChat", 
    description="Chat with your documents",
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# Ensure directories exist
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)
os.makedirs("vector_store", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Global variables for chat management
active_streams = {}
chat_storage = {}

# Startup event for cloud deployment
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("ChatDocs AI starting up...")
    # Ensure all directories exist
    directories = ["data/uploads", "templates", "static", "vector_store", "logs"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    logger.info("All directories initialized")

# Pydantic models
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: str

class ChatRequest(BaseModel):
    message: str
    chat_id: str

class StopRequest(BaseModel):
    chat_id: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main page with chat interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.txt', '.docx')):
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF, TXT, or DOCX files.")
        
        # Create new chat session
        chat_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Save uploaded file
        file_path = f"data/uploads/{chat_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process document
        try:
            # Extract text
            file_handler = FileHandler()
            text = file_handler.extract_text(file_path)
            
            # Chunk text
            chunker = TextChunker()
            chunks = chunker.chunk_text(text)
            
            # Create embeddings and vector store
            embedder = DocumentEmbedder()
            vector_store = embedder.create_vector_store(chunks)
            
            if vector_store is None:
                raise Exception("Failed to create vector store")
            
            # Initialize QA engine
            qa_engine = QAEngine(vector_store)
            
            # Save to database
            db.create_chat(
                chat_id=chat_id,
                title=file.filename,
                document_filename=file.filename,
                document_path=file_path,
                chunks_count=len(chunks)
            )
            
            # Add initial assistant message to database
            db.add_message(
                chat_id=chat_id,
                role="assistant",
                content=f"✅ Document '{file.filename}' processed successfully! I've analyzed {len(chunks)} chunks of text. You can now ask me questions about this document."
            )
            
            # Initialize chat storage (for runtime data)
            chat_storage[chat_id] = {
                "qa_engine": qa_engine,
                "vector_store": vector_store,
            }
            
            return {
                "chat_id": chat_id, 
                "filename": file.filename,
                "chunks_processed": len(chunks),
                "status": "success"
            }
            
        except Exception as processing_error:
            # Clean up file if processing failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Document processing failed: {str(processing_error)}")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_with_document(chat_request: ChatRequest):
    """Stream chat response"""
    chat_id = chat_request.chat_id
    message = chat_request.message
    
    # Check if chat exists in database
    if not db.chat_exists(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Get or recreate QA engine if not in memory
    if chat_id not in chat_storage:
        # Recreate from database
        chat_data = db.get_chat(chat_id)
        if not chat_data:
            raise HTTPException(status_code=404, detail="Chat not found in database")
        
        try:
            # Recreate the QA engine from saved document
            file_handler = FileHandler()
            text = file_handler.extract_text(chat_data['document_path'])
            
            chunker = TextChunker()
            chunks = chunker.chunk_text(text)
            
            embedder = DocumentEmbedder()
            vector_store = embedder.create_vector_store(chunks)
            
            qa_engine = QAEngine(vector_store)
            
            chat_storage[chat_id] = {
                "qa_engine": qa_engine,
                "vector_store": vector_store,
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to recreate QA engine: {str(e)}")
    
    qa_engine = chat_storage[chat_id].get("qa_engine")
    if not qa_engine:
        raise HTTPException(status_code=500, detail="QA engine not initialized for this chat")
    
    # Add user message to database
    db.add_message(chat_id, "user", message)
    
    # Update chat title if this is the first user message
    user_messages = db.get_chat_messages(chat_id)
    user_message_count = len([msg for msg in user_messages if msg["role"] == "user"])
    if user_message_count == 1:
        title = message[:50] + "..." if len(message) > 50 else message
        db.update_chat_title(chat_id, title)
    
    async def generate_response():
        """Generate streaming response"""
        try:
            # Mark this stream as active
            active_streams[chat_id] = True
            reset_stop()
            
            # Simulate streaming by getting answer and sending it word by word
            # In a real implementation, you'd modify the QA engine to support streaming
            try:
                # Get the answer from QA engine
                answer = qa_engine.answer_question(message)
                
                if not active_streams.get(chat_id, False):
                    yield f"data: {json.dumps({'type': 'stopped', 'content': '[Response stopped by user]'})}\n\n"
                    return
                
                # Split answer into words for streaming effect
                words = answer.split()
                streamed_content = ""
                
                for i, word in enumerate(words):
                    if not active_streams.get(chat_id, False):
                        yield f"data: {json.dumps({'type': 'stopped', 'content': '[Response stopped by user]'})}\n\n"
                        return
                    
                    streamed_content += word + " "
                    yield f"data: {json.dumps({'type': 'token', 'content': word + ' '})}\n\n"
                    
                    # Add delay for streaming effect
                    await asyncio.sleep(0.1)
                
                if active_streams.get(chat_id, False):
                    # Stream completed normally - save to database
                    db.add_message(chat_id, "assistant", answer)
                    yield f"data: {json.dumps({'type': 'complete', 'content': answer})}\n\n"
                
            except Exception as qa_error:
                error_message = f"Error processing your question: {str(qa_error)}"
                yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"
                
                # Add error message to database
                db.add_message(chat_id, "assistant", error_message)
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        finally:
            # Clean up
            if chat_id in active_streams:
                del active_streams[chat_id]
    
    return StreamingResponse(generate_response(), media_type="text/plain")

@app.post("/stop")
async def stop_chat(stop_request: StopRequest):
    """Stop ongoing chat response"""
    chat_id = stop_request.chat_id
    
    if chat_id in active_streams:
        active_streams[chat_id] = False
        stop_generation()  # Stop the QA engine generation
        return {"status": "stopped"}
    
    return {"status": "no active stream found"}

@app.get("/chats")
async def get_chat_history():
    """Get all chat histories from database"""
    try:
        chats = db.get_all_chats()
        formatted_chats = []
        
        for chat in chats:
            formatted_chats.append({
                "id": chat["id"],
                "title": chat["title"],
                "created_at": chat["created_at"],
                "message_count": chat["message_count"],
                "document": chat.get("document_filename", ""),
                "chunks_count": chat.get("chunks_count", 0)
            })
        
        return {"chats": formatted_chats}
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return {"chats": []}

@app.get("/chats/{chat_id}")
async def get_chat_messages(chat_id: str):
    """Get messages for a specific chat from database"""
    try:
        chat_with_messages = db.get_chat_with_messages(chat_id)
        if not chat_with_messages:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Format messages for frontend
        formatted_messages = []
        for msg in chat_with_messages["messages"]:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            })
        
        return {
            "id": chat_with_messages["id"],
            "title": chat_with_messages["title"],
            "messages": formatted_messages,
            "document": chat_with_messages.get("document_filename", ""),
            "chunks_count": chat_with_messages.get("chunks_count", 0),
            "created_at": chat_with_messages["created_at"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat messages for {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get chat messages")

@app.delete("/chats/{chat_id}")
async def delete_chat(chat_id: str):
    """Delete a chat and its associated document"""
    try:
        # Get chat data before deletion
        chat_data = db.get_chat(chat_id)
        if not chat_data:
            raise HTTPException(status_code=404, detail="Chat not found")
        
        # Stop any active stream
        if chat_id in active_streams:
            active_streams[chat_id] = False
            stop_generation()
        
        # Remove from memory storage
        if chat_id in chat_storage:
            del chat_storage[chat_id]
        
        # Remove document file if it exists
        if chat_data.get("document_path"):
            file_path = chat_data["document_path"]
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.info(f"Deleted file: {file_path}")
                except Exception as e:
                    logger.warning(f"Could not delete file {file_path}: {e}")
        
        # Delete from database (this will cascade delete messages)
        if db.delete_chat(chat_id):
            return {"status": "deleted"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete chat from database")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat {chat_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete chat")

@app.get("/health")
async def health_check():
    """Health check endpoint with comprehensive system status"""
    try:
        # Check environment variables
        env_status = {
            "google_api_key": bool(os.getenv("GOOGLE_API_KEY")),
            "port": os.getenv("PORT", "8000"),
            "python_version": os.getenv("PYTHON_VERSION", "Unknown")
        }
        
        # Check database
        try:
            db_stats = db.get_stats()
            db_status = "healthy"
        except Exception as db_error:
            db_stats = {"error": str(db_error)}
            db_status = "unhealthy"
        
        # Overall health status
        overall_status = "healthy" if env_status["google_api_key"] and db_status == "healthy" else "degraded"
        
        return {
            "status": overall_status,
            "environment": env_status,
            "database": {
                "status": db_status,
                "stats": db_stats
            },
            "memory": {
                "active_chats": len(chat_storage),
                "active_streams": len(active_streams)
            },
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        # Return 200 but indicate unhealthy status
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.post("/admin/cleanup")
async def cleanup_old_chats(days_old: int = 30):
    """Admin endpoint to cleanup old chats"""
    try:
        deleted_count = db.cleanup_old_chats(days_old)
        return {
            "status": "success",
            "deleted_chats": deleted_count,
            "message": f"Cleaned up {deleted_count} chats older than {days_old} days"
        }
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
