import json, shutil
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import CHROMA_DIR,KNOWLEDGE_DIR,EMBEDDING_MODEL,TOP_K

def embeddings(): return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
def store(): return Chroma(collection_name='it_helpdesk',persist_directory=str(CHROMA_DIR),embedding_function=embeddings())

def ingest():
    docs=[]
    for p in sorted(KNOWLEDGE_DIR.rglob('*.md')):
        docs.append(Document(page_content=p.read_text(encoding='utf-8'),metadata={'source':str(p.relative_to(KNOWLEDGE_DIR)),'category':p.parent.name}))
    chunks=RecursiveCharacterTextSplitter(chunk_size=700,chunk_overlap=120).split_documents(docs)
    if CHROMA_DIR.exists(): shutil.rmtree(CHROMA_DIR)
    CHROMA_DIR.mkdir(parents=True,exist_ok=True)
    Chroma.from_documents(chunks,embeddings(),collection_name='it_helpdesk',persist_directory=str(CHROMA_DIR))
    return len(docs),len(chunks)

@tool
def search_knowledge_base(query:str)->str:
    """Search the trusted IT troubleshooting knowledge base for procedures and technical guidance."""
    if not CHROMA_DIR.exists() or not any(CHROMA_DIR.iterdir()): return json.dumps({'error':'knowledge base not indexed'})
    docs=store().similarity_search(query,k=TOP_K)
    return json.dumps({'results':[{'source':d.metadata.get('source'),'category':d.metadata.get('category'),'content':d.page_content} for d in docs]},indent=2)
