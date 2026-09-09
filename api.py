from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.agent import graph
app=FastAPI(title='AI IT Helpdesk Agent',version='1.0')
class Request(BaseModel): message:str
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/chat')
def chat(r:Request):
 result=graph.invoke({'messages':[HumanMessage(content=r.message)]})
 for m in reversed(result['messages']):
  if getattr(m,'type',None)=='ai' and m.content: return {'answer':m.content}
 return {'answer':'No answer generated'}
