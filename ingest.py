import os
import shutil
import markitdown
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings  # <--- Switched to Ollama

# Configuration
SOURCE_DIR = "source_docs"
MASTER_FILE = "master_knowledge_base.md"
DB_DIR = "db"
EMBED_MODEL = "nomic-embed-text" # Or your preferred local model

def reset_environment():
    """Cleans up previous runs to ensure a fresh start."""
    print("--- Resetting Environment ---")
    if os.path.exists(MASTER_FILE):
        os.remove(MASTER_FILE)
    if os.path.isdir(DB_DIR):
        shutil.rmtree(DB_DIR)
    print("Environment cleared.")

def build_master_markdown():
    """Converts all source files into one master markdown file."""
    md_converter = markitdown.MarkItDown()
    master_content = []

    if not os.path.exists(SOURCE_DIR):
        print(f"Error: {SOURCE_DIR} directory not found.")
        return False
    
    files = [f for f in os.listdir(SOURCE_DIR) if os.path.isfile(os.path.join(SOURCE_DIR, f))]
    if not files:
        print("No files found.")
        return False

    for filename in files:
        filepath = os.path.join(SOURCE_DIR, filename)
        try:
            print(f"Converting: {filename}")
            result = md_converter.convert(filepath)
            master_content.append(f"\n\n# SOURCE_FILE: {filename}\n\n{result.text_content}\n")
        except Exception as e:
            print(f"Failed {filename}: {e}")

    with open(MASTER_FILE, "w", encoding="utf-8") as f:
        f.writelines(master_content)
    return True

def ingest_to_db():
    """Loads the fresh master markdown file into the vector database using Ollama."""
    print(f"--- Ingesting into DB using Ollama ({EMBED_MODEL}) ---")
    
    loader = UnstructuredMarkdownLoader(MASTER_FILE)
    raw_documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    documents = text_splitter.split_documents(raw_documents)
    
    # Use local Ollama embeddings
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    
    vectordb = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    # Chroma 0.4+ persists automatically, but calling it for safety
    vectordb.persist()
    print(f"--- Successfully ingested {len(documents)} chunks ---")

if __name__ == "__main__":
    reset_environment()
    if build_master_markdown():
        ingest_to_db()