# 1. Create a virtual environment
python -m venv rag_env

# 2. Activate the environment
.\rag_env\Scripts\Activate.ps1

# 3. Upgrade pip and install requirements
python -m pip install --upgrade pip
pip install chromadb langchain langchain-community langchain-huggingface sentence-transformers pypdf python-docx python-magic-bin markdown unstructured[all-docs] tqdm pandas

# 4. Pull the local models via Ollama
# Ensure Ollama is running in your system tray first
ollama pull llama3
ollama pull nomic-embed-text

Write-Host "Setup Complete. Place your resumes in a folder named 'source_docs'." -ForegroundColor Green