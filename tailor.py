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
    SYSTEM: You are a Recruitment Optimization Engine. Your goal is to map a Candidate's actual career data to a specific Job Description (JD).
    
    STRICT OPERATIONAL RULES:
    1. SOURCE TRUTH: Use ONLY the information provided in the "Retrieved Context" below. 
    2. NO EXTRAPOLATION: If a requirement in the JD is not explicitly supported by the Context, DO NOT include it in the output. 
    3. NO HALLUCINATION: Do not invent projects, dates, or technical proficiencies. If the context is silent on a skill, that skill does not exist for this output.
    4. STRUCTURE: Organize the output by Professional Experience (Chronological), followed by a Technical Skills alignment.
    5. FORMATTING: Use professional, concise bullet points. Maintain original Job Titles and Company names as found in the context.

    JOB DESCRIPTION:
    {question}

    RETRIEVED CONTEXT (CANDIDATE DATA):
    {context}

    TAILORED OUTPUT:
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
                "k": 15,             # Increased to 15 to capture more detailed job blocks
                "fetch_k": 50,       # Initial pool of 50 candidates
                "lambda_mult": 0.7   # Increased to allow for more semantic similarity and capture details
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