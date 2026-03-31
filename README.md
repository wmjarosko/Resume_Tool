# Local RAG-Based Resume Tailoring System

This is a local, privacy-preserving resume tailoring system that uses Retrieval-Augmented Generation (RAG) to customize your career data to specific job descriptions. It is built entirely on local components using **LangChain**, **ChromaDB**, and **Ollama** models, ensuring none of your personal data leaves your machine.

## Features

- **Local Vector Database:** Uses ChromaDB to store embedded career data locally.
- **Local Models (Ollama):**
  - Embeddings: `nomic-embed-text`
  - Generation: `mistral` (default, customizable)
- **Document Ingestion:** Automatically converts markdown files from the `source_docs` directory into a master knowledge base and ingests them into the vector database.
- **Tailored Outputs:** Generates customized resumes based on a target job description (`job_description.txt`), outputting both:
  - **Human-Readable:** `Tailored_Resume_Human.docx`
  - **ATS-Optimized:** `Tailored_Resume_ATS.md`

## Setup

### Prerequisites

1. Install Python (3.10+ recommended).
2. Install [Ollama](https://ollama.com/) and ensure the service is running.

### Installation

**Using the provided PowerShell script (Windows):**

1. Run the setup script to create a virtual environment, install dependencies, and pull the necessary Ollama models:
   ```powershell
   .\resume_tool.ps1
   ```
   *Note: The script currently pulls `llama3` and `nomic-embed-text`. If you want to use the default `mistral` model configured in `tailor.py`, you will need to pull it manually: `ollama pull mistral`.*

**Manual Installation (Any OS):**

1. Create a virtual environment using `python -m venv rag_env`
   ```bash
   source rag_env/bin/activate  # On Windows: .\rag_env\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Pull the required models using Ollama:
   ```bash
   ollama pull nomic-embed-text
   ollama pull mistral
   ```

## Usage

1. **Prepare Source Documents:** Place your resume and career data files (in Markdown format or other supported document formats) into a directory named `source_docs/`.
2. **Ingest Data:** Run the ingestion script to process the documents and build the vector database:
   ```bash
   python ingest.py
   ```
3. **Prepare Job Description:** Create a file named `job_description.txt` in the root directory and paste the target job description into it.
4. **Tailor Resume:** Run the tailoring script to generate your customized resume:
   ```bash
   python tailor.py
   ```

The script will produce `Tailored_Resume_Human.docx` and `Tailored_Resume_ATS.md` in the root directory.

## Configuration

- **`ingest.py`**: You can change the embedding model by modifying the `EMBED_MODEL` variable (default is `nomic-embed-text`).
- **`tailor.py`**: You can change the generation model by modifying the `MODEL_NAME` variable (default is `mistral`). You can also adjust the retrieval parameters (`k`, `fetch_k`, `lambda_mult`) inside the `RetrievalQA` setup.
