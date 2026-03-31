import os
from docx import Document
from langchain_chroma import Chroma
#from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import OllamaLLM
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from docx.shared import Pt

# Configuration
DB_DIR = "./db"
MODEL_NAME = "mistral" 
JD_FILE = "job_description.txt"

def save_as_docx(text_content, filename="Tailored_Resume.docx", is_ats=False):
    """
    Converts LLM output into a Word Document.
    If is_ats=True, it uses a simplified, single-column standard layout.
    """
    doc = Document()
    
    # Standard ATS-friendly font (Arial or Calibri)
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    lines = text_content.split('\n')
    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
            
        if clean_line.startswith('#'):
            level = clean_line.count('#')
            content = clean_line.replace('#', '').strip()
            # ATS version uses bold text rather than fancy Word Header styles
            if is_ats:
                p = doc.add_paragraph()
                run = p.add_run(content.upper())
                run.bold = True
                p.style = doc.styles['Normal']
            else:
                doc.add_heading(content, level=min(level, 9))
        elif clean_line.startswith('*') or clean_line.startswith('-'):
            content = clean_line[1:].strip()
            doc.add_paragraph(content, style='List Bullet')
        else:
            doc.add_paragraph(clean_line)

    doc.save(filename)
    print(f"{'ATS-Optimized' if is_ats else 'Professional'} DOCX created: {os.path.abspath(filename)}")

def get_tailored_resume(job_description):
    if not os.path.exists(DB_DIR):
        print("Error: Vector database not found. Run ingest.py first.")
        return

    EMBED_MODEL = "nomic-embed-text"
    embeddings = OllamaEmbeddings(model=EMBED_MODEL)
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)

    prompt_template = """
    SYSTEM: You are a professional resume writer. Your task is to rewrite a resume to align with a specific Job Description.
    
    STRICT RULES:
    1. Use ONLY the facts provided in the "Retrieved Resume Context" below.
    2. Do NOT add skills, certifications, or job titles that are not explicitly mentioned in the context.
    3. Re-phrase and prioritize the user's existing experience to highlight keywords found in the Job Description.
    4. If the user lacks a specific skill requested in the Job Description, simply omit it.
    5. Output the result in a clean, professional text format suitable for a DOCX or PDF.

    JOB DESCRIPTION:
    {question}

    RETRIEVED RESUME CONTEXT:
    {context}

    TAILORED RESUME:
    """

    PROMPT = PromptTemplate(
        template=prompt_template, 
        input_variables=["context", "question"]
    )

    llm = OllamaLLM(model=MODEL_NAME)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 2,             # Pull enough to cover all roles
                "fetch_k": 40,       # Initial search pool
                "lambda_mult": 0.7   # Lowering this (from 0.8) FORCES more diversity
                             # and prevents it from only pulling one 'era'.
            }
        ), # <--- The parenthesis for as_retriever must close here
        chain_type_kwargs={"prompt": PROMPT}
    )

    print(f"Synthesizing career data using {MODEL_NAME}...")
    response = qa_chain.invoke({"query": job_description})
    return response["result"]

if __name__ == "__main__":
    if os.path.exists(JD_FILE):
        with open(JD_FILE, "r", encoding="utf-8") as f:
            jd_content = f.read()
            
        result = get_tailored_resume(jd_content)
        
        # 1. Save the Professional Version (Best for humans)
        save_as_docx(result, "Tailored_Resume_Human.docx", is_ats=False)
        
        # 2. Save the ATS Version (Best for portal uploads)
        save_as_docx(result, "Tailored_Resume_ATS.docx", is_ats=True)
    else:
        print(f"Please create {JD_FILE} first.")