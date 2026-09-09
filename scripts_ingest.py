from app.rag import ingest
n,c=ingest();print(f'Indexed {n} documents into {c} chunks.')
