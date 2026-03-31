# Resume Tailoring System (Local RAG)

This system uses a Local Retrieval-Augmented Generation (RAG) workflow to rewrite resumes based on specific job descriptions. It runs entirely locally using Ollama for both embeddings and text generation, ensuring your data remains private and secure.

## Prerequisites

1.  **Ollama**: Download and install [Ollama](https://ollama.com/).
2.  **Models**: Pull the required local models via your terminal:

```powershell
ollama pull mistral
ollama pull nomic-embed-text
```

## Installation

1.  **Create & Activate Virtual Environment**:

```powershell
python3 -m venv rag_env
.\rag_env\Scripts\Activate.ps1
```

*(On macOS/Linux, use `source rag_env/bin/activate` instead)*

2.  **Install Dependencies**:

```powershell
pip install -r requirements.txt
```

## Project Structure

*   `source_docs/`: Drop your master resume documents (DOCX, PDF, or TXT) here.
*   `job_description.txt`: Paste the target job description into this file.
*   `ingest.py`: Converts source documents to a master Markdown file and populates the vector database.
*   `tailor.py`: Queries the database and generates tailored resumes based on the job description.

## Workflow

### 1. Ingest (The "Clean Sweep")

Run `ingest.py` whenever you add new source documents or want to reset the system.

**What it does:** Deletes the existing `db/` folder and `master_knowledge_base.md`, converts all files in `source_docs/` to Markdown, and creates fresh vector embeddings using `nomic-embed-text`.

```powershell
python ingest.py
```

### 2. Tailor

Ensure your target job description is in `job_description.txt`, then run the tailoring script.

**What it does:** Uses the `mistral` model to rewrite your experience based on the job description. It generates two files:

*   **Tailored_Resume_Human.docx**: Formatted with professional headings.
*   **Tailored_Resume_ATS.docx**: A simplified, bold-text-only version optimized for Applicant Tracking Systems.

```powershell
python tailor.py
```

## Technical Notes

*   **Embedding Dimension**: This system uses `nomic-embed-text`, which relies on 768 dimensions.
*   **MMR Retrieval**: `tailor.py` uses Maximal Marginal Relevance (MMR). This is configured to balance semantic similarity with diversity in the search results, ensuring the AI captures continuous job blocks while still referencing different experiences across your career.
*   **Consistency**: Both scripts are hardcoded to use `nomic-embed-text` to prevent dimension mismatch errors.
