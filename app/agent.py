from typing import Annotated,TypedDict
import operator
from langchain_core.messages import AnyMessage,SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph,START
from langgraph.prebuilt import ToolNode,tools_condition
from app.config import OLLAMA_MODEL,OLLAMA_BASE_URL
from app.rag import search_knowledge_base
from app.tools import check_network,ping_host,dns_lookup,system_info,disk_space,memory_usage
TOOLS=[search_knowledge_base,check_network,ping_host,dns_lookup,system_info,disk_space,memory_usage]
PROMPT='''You are a safe AI IT Helpdesk Agent. Use the knowledge base for technical procedures and use read-only tools for live diagnostics. Never invent tool results. Explain symptoms, observations, likely cause, and recommended steps. If evidence is insufficient, ask a focused question. Never use arbitrary shell commands or perform destructive/state-changing operations.'''
model=ChatOllama(model=OLLAMA_MODEL,base_url=OLLAMA_BASE_URL,temperature=0).bind_tools(TOOLS)
class State(TypedDict): messages:Annotated[list[AnyMessage],operator.add]
def assistant(state): return {'messages':[model.invoke([SystemMessage(content=PROMPT)]+state['messages'])]}
b=StateGraph(State); b.add_node('assistant',assistant); b.add_node('tools',ToolNode(TOOLS,handle_tool_errors=True)); b.add_edge(START,'assistant'); b.add_conditional_edges('assistant',tools_condition); b.add_edge('tools','assistant'); graph=b.compile()
