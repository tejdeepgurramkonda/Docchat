import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Check if API key is set
api_key = os.getenv('GOOGLE_API_KEY')
print(f'API Key exists: {bool(api_key)}')
print(f'API Key length: {len(api_key) if api_key else 0}')
print(f'API Key starts with AIzaSy: {api_key.startswith("AIzaSy") if api_key else False}')

if not api_key:
    print("❌ No API key found in environment variables")
    exit(1)

# Test the API connection
try:
    llm = GoogleGenerativeAI(
        model='gemini-2.0-flash-exp',
        google_api_key=api_key,
        temperature=0.7
    )
    
    # Simple test query
    print("Testing API connection...")
    response = llm.invoke('Hello, this is a test. Please respond with just: API working')
    print(f'✓ API Test Successful: {response}')
    
except Exception as e:
    print(f'✗ API Test Failed: {str(e)}')
    print(f'Error type: {type(e).__name__}')
    
    # Check if it's a quota issue
    if '500 Internal error encountered' in str(e) or 'internal error' in str(e).lower():
        print("\n🔍 This appears to be a Google API internal error.")
        print("Even with a Pro plan, this can happen due to:")
        print("1. Temporary API service issues")
        print("2. Regional API availability")
        print("3. Model-specific issues with gemini-2.0-flash-exp")
        print("\nTrying with a more stable model...")
        
        try:
            llm_stable = GoogleGenerativeAI(
                model='gemini-1.5-pro',
                google_api_key=api_key,
                temperature=0.7
            )
            response = llm_stable.invoke('Hello, this is a test. Please respond with just: API working')
            print(f'✓ Stable model test successful: {response}')
        except Exception as e2:
            print(f'✗ Stable model test also failed: {str(e2)}')
