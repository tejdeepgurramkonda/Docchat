# DOCChat Setup Instructions

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Environment Variables**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## Environment Setup

### Option 1: Using pip (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Using conda
```bash
# Create conda environment
conda create -n docchat python=3.9

# Activate environment
conda activate docchat

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Google API Key
1. Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Add it to your `.env` file:
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```

### Custom Configuration
You can modify the following settings in `.env`:
- `MODEL_NAME`: Google Gemini model to use (default: gemini-2.5-pro)
- `CHUNK_SIZE`: Text chunk size for processing (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `MAX_FILE_SIZE_MB`: Maximum file size allowed (default: 100)

## Usage

1. **Upload a Document**
   - Click "Choose a file" in the sidebar
   - Select a PDF, DOCX, or TXT file
   - Click "Process Document"

2. **Ask Questions**
   - Type your question in the chat input
   - Get AI-powered answers based on your document

3. **Features**
   - Real-time chat interface
   - Document summarization
   - Source citation
   - Multi-format support

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check if you're using the correct Python environment

2. **API Key Issues**
   - Verify your Google API key is correct
   - Check if you have enabled the Gemini API in your Google Cloud Console
   - Ensure your API key has the necessary permissions

3. **File Upload Issues**
   - Ensure file size is under the limit (100MB by default)
   - Check if file format is supported (PDF, DOCX, TXT)

4. **Memory Issues**
   - Reduce chunk size in `.env` file
   - Process smaller documents
   - Consider using a machine with more RAM

### Log Files
Check `logs/usage.log` for detailed error messages and application logs.

## Development

### Project Structure
```
docchat/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── utils/                  # Utility modules
│   ├── file_handler.py     # File processing
│   ├── chunker.py          # Text chunking
│   ├── embedder.py         # Document embedding
│   └── qa_engine.py        # Question answering
├── data/uploads/           # Uploaded files
├── vector_store/           # Vector indices
└── logs/                   # Application logs
```

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Implement changes
3. Test thoroughly
4. Update documentation
5. Submit pull request

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review logs in `logs/usage.log`
3. Open an issue on GitHub
4. Contact support team

## License

This project is licensed under the MIT License.
