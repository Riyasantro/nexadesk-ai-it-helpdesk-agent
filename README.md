# NexaDesk – AI IT Helpdesk Agent

Full IBM Agentic AI internship project: Streamlit UI + LangGraph + Ollama + RAG/ChromaDB + read-only diagnostic tools + SQLite memory + FastAPI.

## Ubuntu setup
```bash
cd ai-it-helpdesk-final
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
ollama serve
# in another terminal
ollama pull qwen3.5:9b
python scripts_ingest.py
streamlit run streamlit_app.py
```

If your Ollama model has a different name, change `OLLAMA_MODEL` in `.env`.

## Optional API
```bash
uvicorn api:app --reload
```

## Test
```bash
pytest -q
```

The default tools are read-only. No arbitrary shell tool is exposed to the LLM.
