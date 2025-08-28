# ChatDocs AI - Complete Documentation

A sophisticated web application that allows users to upload documents, chat with them using AI, manage chat history, stop responses mid-way, and delete chats/documents with persistent storage.

## 🚀 Features Implemented

### ✅ Core Features
- **Document Upload & Storage** - Upload PDF, TXT, DOCX files
- **AI-Powered Chat** - Chat with documents using Google Gemini
- **Persistent Chat History** - SQLite database storage
- **Stop Mid-Response** - Cancel AI responses like ChatGPT
- **Delete Chats/Documents** - Complete cleanup with trash icons
- **Real-time Streaming** - Token-by-token response streaming
- **Vector Search** - FAISS-based similarity search
- **Document Processing** - Chunking and embedding generation

### ✅ UI/UX Features
- **Clean Modern Interface** - HTML + CSS + JavaScript
- **Sidebar Navigation** - Chat history with hover effects
- **Responsive Design** - Works on different screen sizes
- **Status Indicators** - Upload progress and error handling
- **Trash Icons** - Appear on hover for easy deletion
- **Auto-scroll Chat** - Messages scroll automatically
- **Input Auto-resize** - Textarea expands with content

### ✅ Technical Features
- **FastAPI Backend** - High-performance async API
- **SQLite Database** - Persistent storage with proper schemas
- **Google Gemini Integration** - Latest AI models (gemini-2.5-pro)
- **FAISS Vector Store** - Efficient similarity search
- **Streaming Responses** - Real-time token streaming
- **Error Handling** - Comprehensive error management
- **Logging** - Detailed application logging
- **Environment Configuration** - .env file support

## 📁 Project Structure

```
docchat/
├── app.py                 # Main FastAPI application
├── database.py            # SQLite database handler
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables
├── templates/
│   └── index.html        # Frontend UI
├── utils/
│   ├── __init__.py
│   ├── file_handler.py   # Document processing
│   ├── chunker.py        # Text chunking
│   ├── embedder.py       # Vector embeddings
│   └── qa_engine.py      # Q&A with streaming
├── data/
│   ├── uploads/          # Uploaded documents
│   └── docchat.db        # SQLite database
├── logs/
│   └── usage.log         # Application logs
└── vector_store/         # FAISS indices
```

## 🛠 Installation & Setup

### 1. Clone and Navigate
```bash
cd "c:\Users\Lenovo\Music\DOCChat\docchat"
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn[standard] jinja2 python-multipart python-dotenv
pip install google-generativeai langchain langchain-google-genai langchain-community
pip install faiss-cpu PyMuPDF python-docx tiktoken
```

### 3. Configure Environment
The `.env` file is already configured with:
```env
GOOGLE_API_KEY=AIzaSyDWrDN42CWTqAAISwTfmfVpYjyJIxatKrs
MODEL_NAME=gemini-2.5-pro
TEMPERATURE=0.7
MAX_TOKENS=100000
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 4. Run Application
```bash
python -m uvicorn app:app --reload --port 8000
```

### 5. Access Application
Open: http://127.0.0.1:8000

## 🎯 API Endpoints

### Document Management
- `POST /upload` - Upload and process documents
- `DELETE /chats/{chat_id}` - Delete chat and document

### Chat Operations
- `POST /chat` - Stream chat responses
- `POST /stop` - Stop ongoing responses
- `GET /chats` - Get all chat history
- `GET /chats/{chat_id}` - Get specific chat messages

### System
- `GET /health` - Health check with database stats
- `POST /admin/cleanup` - Cleanup old chats

## 💾 Database Schema

### Chats Table
```sql
CREATE TABLE chats (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    document_filename TEXT,
    document_path TEXT,
    chunks_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Messages Table
```sql
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats (id) ON DELETE CASCADE
);
```

## 🔧 Key Components

### 1. FastAPI Application (`app.py`)
- **Async endpoints** for high performance
- **Streaming responses** for real-time chat
- **Error handling** with proper HTTP status codes
- **Database integration** for persistence
- **File management** for uploads and cleanup

### 2. Database Handler (`database.py`)
- **SQLite operations** with proper error handling
- **CRUD operations** for chats and messages
- **Foreign key constraints** for data integrity
- **Indexing** for performance
- **Stats and cleanup** utilities

### 3. Document Processing (`utils/`)
- **FileHandler** - Extract text from PDF, DOCX, TXT
- **TextChunker** - Split documents into searchable chunks
- **DocumentEmbedder** - Generate vector embeddings
- **QAEngine** - Answer questions with context

### 4. Frontend (`templates/index.html`)
- **Modern CSS styling** with hover effects
- **JavaScript streaming** for real-time responses
- **Abort controllers** for stopping requests
- **Dynamic UI updates** for chat management

## 🚀 Usage Examples

### 1. Upload Document
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('/upload', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(`Chat ID: ${result.chat_id}`);
```

### 2. Send Chat Message
```javascript
const response = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        message: "What is this document about?",
        chat_id: "20250828_124001_956379"
    })
});

// Handle streaming response
const reader = response.body.getReader();
// ... stream processing
```

### 3. Stop Response
```javascript
await fetch('/stop', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: currentChatId })
});
```

## 🔒 Security Features

- **File type validation** - Only allow safe document types
- **File size limits** - Prevent large uploads
- **SQL injection protection** - Parameterized queries
- **XSS prevention** - Proper content escaping
- **Error handling** - No sensitive information leakage

## 📊 Performance Features

- **Vector similarity search** - Fast document retrieval
- **Database indexing** - Optimized queries
- **Memory management** - Efficient chat storage
- **Streaming responses** - Better user experience
- **Async operations** - High concurrency support

## 🐛 Debugging & Monitoring

### Health Check
```bash
curl http://127.0.0.1:8000/health
```

### Database Stats
The health endpoint returns:
- Total chats in database
- Total messages stored
- Active chats in memory
- Active streaming sessions

### Logs
Application logs are stored in `logs/usage.log`

## 🧹 Maintenance

### Cleanup Old Chats
```bash
curl -X POST "http://127.0.0.1:8000/admin/cleanup?days_old=30"
```

### Database Backup
```bash
cp data/docchat.db data/docchat_backup_$(date +%Y%m%d).db
```

## 🔮 Future Enhancements

### Potential Improvements
1. **User Authentication** - Multi-user support
2. **Document Sharing** - Share chats between users
3. **Export Chat** - Download conversation history
4. **Multiple File Upload** - Process multiple documents per chat
5. **Advanced Search** - Search across all chats
6. **Document Annotations** - Highlight relevant sections
7. **API Rate Limiting** - Prevent abuse
8. **Docker Deployment** - Containerized deployment
9. **Cloud Storage** - S3/Azure blob storage integration
10. **Advanced Analytics** - Usage statistics and insights

### Performance Optimizations
1. **Vector Store Persistence** - Cache embeddings to disk
2. **Database Connection Pooling** - Better concurrent access
3. **CDN Integration** - Faster static file serving
4. **Background Tasks** - Async document processing
5. **Caching Layer** - Redis for frequent queries

## 📄 License

This project is developed for educational and demonstration purposes.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

---

**Status: ✅ COMPLETE & FUNCTIONAL**

The ChatDocs AI application is fully implemented with all requested features:
- ✅ Document upload and processing
- ✅ AI-powered chat with streaming
- ✅ Persistent chat history
- ✅ Stop responses mid-way
- ✅ Delete chats and documents
- ✅ Modern UI with hover effects
- ✅ Database storage
- ✅ Error handling
- ✅ Health monitoring

**Access the application at: http://127.0.0.1:8000**
