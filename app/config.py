import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
CHROMA_DIR=Path(os.getenv('CHROMA_DIR',str(DATA/'chroma')))
SQLITE_DB=Path(os.getenv('SQLITE_DB',str(DATA/'helpdesk.db')))
KNOWLEDGE_DIR=ROOT/'knowledge'
OLLAMA_MODEL=os.getenv('OLLAMA_MODEL','qwen3.5:9b')
OLLAMA_BASE_URL=os.getenv('OLLAMA_BASE_URL','http://localhost:11434')
EMBEDDING_MODEL=os.getenv('EMBEDDING_MODEL','sentence-transformers/all-MiniLM-L6-v2')
TOP_K=int(os.getenv('TOP_K','4'))
