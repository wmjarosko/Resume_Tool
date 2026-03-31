
Gemini said
Your resume tailoring system is now properly synchronized to use local Ollama embeddings and LLMs. Below are the two files required to standardize your environment and document the workflow for your "fresh start."

Requirements File
Create a file named requirements.txt in your root directory. This includes the specific LangChain-Ollama integration and the markitdown utility used in your ingest.py.

Plaintext
# Core Logic & Vector Database
langchain==0.3.0
langchain-community==0.3.0
langchain-ollama==0.2.0
chromadb==0.5.5

# Document Processing & Conversion
markitdown==0.0.1
unstructured[all-docs]==0.15.13
python-docx==1.1.2
pypdf==5.0.1

# Utilities
python-dotenv==1.0.1
tqdm==4.66.5
pandas==2.2.2
Readme File
This README.md outlines the "Clean Sweep" architecture you've implemented, ensuring that every run starts with a fresh database to prevent context drift.

Resume Tailoring System (Local RAG)
This system uses a Local RAG (Retrieval-Augmented Generation) workflow to rewrite resumes based on specific job descriptions. It runs entirely locally using Ollama for both embeddings and text generation, ensuring your data remains private.

Prerequisites
Ollama: Download and install Ollama.

Models: Pull the required models via your terminal:

PowerShell
ollama pull mistral
ollama pull nomic-embed-text
Installation
Create & Activate Virtual Environment:

PowerShell
python -m venv rag_env
.\rag_env\Scripts\Activate.ps1
Install Dependencies:

PowerShell
pip install -r requirements.txt
Project Structure
source_docs/: Drop your master resume (DOCX, PDF, or TXT) here.

job_description.txt: Paste the target job description into this file.

ingest.py: Converts source documents to a master Markdown file and populates the vector database.

tailor.py: Queries the database and generates tailored resumes.

Workflow
1. Ingest (The "Clean Sweep")
Run ingest.py whenever you add new source documents or want to reset the system.

What it does: Deletes the existing db/ folder and master_knowledge_base.md, converts all files in source_docs/ to Markdown, and creates fresh vector embeddings using nomic-embed-text.

PowerShell
python ingest.py
2. Tailor
Ensure your target job description is in job_description.txt, then run the tailoring script.

What it does: Uses mistral to rewrite your experience. It generates two files:

Tailored_Resume_Human.docx: Formatted with professional headings.

Tailored_Resume_ATS.docx: A simplified, bold-text-only version optimized for Applicant Tracking Systems.

PowerShell
python tailor.py
Technical Notes
Embedding Dimension: This system is locked to 768 dimensions (required by nomic-embed-text).

MMR Retrieval: tailor.py uses Maximal Marginal Relevance (MMR). This is configured to force diversity in the search results, ensuring the AI sees experience from different "eras" of your career rather than just the most recent role.

Consistency: Both scripts are hardcoded to use nomic-embed-text to prevent dimension mismatch errors.
