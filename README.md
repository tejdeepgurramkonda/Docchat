# 🧠 DOCChat - Chat with Your Documents

An intelligent assistant that allows users to upload doc5. **Query Processing**: Convert user questions to embeddings
6. **Semantic Search**: Find relevant document chunks
7. **Response Generation**: Use Gemini to generate contextual answersnts (PDF, DOCX, TXT) and interact with them through natural language queries. Powered by Google Gemini API and advanced RAG (Retrieval-Augmented Generation) technology.

## 🚀 Features

- **Multi-format Support**: Upload PDF, DOCX, and TXT files
- **Intelligent Chat**: Ask questions and get contextual answers from your documents
- **Advanced RAG**: Uses vector embeddings and semantic search for accurate responses
- **Modern UI**: Clean, responsive Streamlit interface
- **Real-time Processing**: Fast document processing and query responses
- **Chat History**: Maintains conversation context within sessions

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python, LangChain
- **LLM**: Google Gemini 2.5 Pro
- **Vector Store**: FAISS
- **Document Processing**: PyMuPDF, python-docx
- **Embeddings**: Google Gemini Embeddings

## 📁 Project Structure

```
docchat/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Dependencies
├── .env                    # API keys and config
├── README.md               # Project documentation
├── utils/
│   ├── file_handler.py     # File reading (PDF, DOCX, TXT)
│   ├── chunker.py          # Text splitting logic
│   ├── embedder.py         # Embedding logic
│   └── qa_engine.py        # RAG + GPT-powered response
├── data/
│   └── uploads/            # Uploaded documents
├── vector_store/
│   └── faiss_index.pkl     # Saved vector index
└── logs/
    └── usage.log           # Optional usage log
```

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd docchat
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Google API key:
     ```
     GOOGLE_API_KEY=your_google_api_key_here
     ```

## 🚀 Usage

1. **Start the application**:
   ```bash
   streamlit run app.py
   ```

2. **Upload a document**:
   - Use the sidebar to upload PDF, DOCX, or TXT files
   - Click "Process Document" to analyze the file

3. **Start chatting**:
   - Ask questions about your document in the chat interface
   - Get intelligent, context-aware responses

## 📝 Example Use Cases

- **Students**: Chat with textbooks, research papers, or lecture notes
- **Lawyers**: Analyze legal documents and contracts
- **Researchers**: Extract insights from academic papers
- **Professionals**: Quickly understand business documents
- **Writers**: Analyze and reference source materials

## 🔍 How It Works

1. **Document Upload**: Users upload PDF, DOCX, or TXT files
2. **Text Extraction**: Extract text content from documents
3. **Text Chunking**: Split text into manageable chunks (1000 tokens)
4. **Embedding**: Create vector embeddings for each chunk
5. **Vector Storage**: Store embeddings in FAISS vector database
6. **Query Processing**: Convert user questions to embeddings
7. **Semantic Search**: Find relevant document chunks
8. **Response Generation**: Use GPT-4 to generate contextual answers

## 🎯 Roadmap

### Phase 1: Core Features ✅
- [x] Document upload and processing
- [x] Basic chat interface
- [x] RAG implementation

### Phase 2: Enhancements 🔄
- [ ] Multi-document support
- [ ] Chat history persistence
- [ ] Document annotation
- [ ] Export responses to PDF/Word

### Phase 3: Advanced Features 🔮
- [ ] User authentication
- [ ] Document management dashboard
- [ ] API endpoints
- [ ] Mobile-responsive design

### Phase 4: Enterprise Features 🏢
- [ ] Team collaboration
- [ ] Analytics dashboard
- [ ] Custom model fine-tuning
- [ ] On-premise deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google for Gemini API
- LangChain for RAG framework
- Streamlit for the web interface
- FAISS for vector storage

## 📞 Support

For support, please open an issue on GitHub or contact [your-email@example.com]

---

**DOCChat** - Making document interaction intelligent and intuitive! 🚀
