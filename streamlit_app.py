import uuid
import json
from datetime import datetime

import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from app.agent import graph
from app.memory import init, load, save, clear
from app.config import OLLAMA_MODEL, CHROMA_DIR, KNOWLEDGE_DIR

st.set_page_config(page_title="NexaDesk | AI IT Support", page_icon="🛡️", layout="wide", initial_sidebar_state="expanded")
init()

if "sid" not in st.session_state: st.session_state.sid = str(uuid.uuid4())
if "messages" not in st.session_state: st.session_state.messages = load(st.session_state.sid)
if "tool_events" not in st.session_state: st.session_state.tool_events = []
if "last_latency" not in st.session_state: st.session_state.last_latency = None

def rag_ready(): return CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir())
def knowledge_count(): return len(list(KNOWLEDGE_DIR.rglob("*.md"))) if KNOWLEDGE_DIR.exists() else 0
def display_name(tool_name):
    names={"check_network":"Network interface check","ping_host":"Connectivity test","dns_lookup":"DNS resolution","system_info":"System information","disk_space":"Disk usage","memory_usage":"Memory usage","search_knowledge_base":"Knowledge-base search"}
    return names.get(tool_name, tool_name.replace("_"," ").title())
def icon_for(tool_name):
    if "network" in tool_name or "ping" in tool_name or "dns" in tool_name: return "🌐"
    if "disk" in tool_name: return "💾"
    if "memory" in tool_name: return "🧠"
    if "system" in tool_name: return "💻"
    return "🔎"

st.markdown("""
<style>
:root{--ink:#e8edf5;--muted:#9aa6b8;--panel:#111722;--line:#273244}
[data-testid="stAppViewContainer"]{background:#0b1018}[data-testid="stHeader"]{background:rgba(11,16,24,.86)}
[data-testid="stSidebar"]{background:#0d131d;border-right:1px solid #202a39}[data-testid="stSidebarContent"]{padding-top:1.4rem}
.block-container{max-width:1380px;padding-top:1.6rem;padding-bottom:4rem}
.brand{display:flex;align-items:center;gap:12px;margin-bottom:4px}.brand-mark{width:42px;height:42px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#315efb,#8b5cf6);box-shadow:0 8px 30px rgba(70,90,255,.22);font-size:22px}.brand-name{font-size:20px;font-weight:760}.brand-sub{color:var(--muted);font-size:12px;margin-top:1px}
.hero-title{font-size:36px;font-weight:800;letter-spacing:-1.2px;margin:0}.hero-sub{color:#8996aa;font-size:15px;margin-top:5px}
.status{display:inline-flex;align-items:center;gap:7px;padding:5px 10px;border:1px solid #263245;border-radius:999px;background:#101722;color:#b9c4d5;font-size:12px}.dot{width:7px;height:7px;border-radius:50%;background:#36d399;box-shadow:0 0 10px rgba(54,211,153,.55)}
.metric-card{background:linear-gradient(145deg,#131a25,#101620);border:1px solid #263143;border-radius:14px;padding:16px 18px;min-height:98px}.metric-label{color:#8f9bad;font-size:12px;text-transform:uppercase;letter-spacing:.08em}.metric-value{font-size:22px;font-weight:750;margin-top:8px}.metric-note{color:#68758a;font-size:11px;margin-top:4px}
.section-title{font-size:15px;font-weight:700;margin:2px 0 10px}.quick{border:1px solid #283449;background:#111925;border-radius:12px;padding:12px 14px;color:#c4cedd;min-height:70px}.quick strong{color:#edf2f8;display:block;margin-bottom:3px}.quick span{color:#78869b;font-size:12px}.sidebar-title{font-weight:700;color:#e7edf6;margin-top:10px}.sidebar-small{color:#78869b;font-size:11px}
[data-testid="stChatMessage"]{border:1px solid #222d3e;background:#101721;border-radius:14px;padding:10px 14px;margin-bottom:10px}[data-testid="stChatMessage"] p{font-size:14px;line-height:1.65}div[data-testid="stChatInput"] textarea{background:#111925!important}.stButton>button{border-radius:10px;border:1px solid #2a3548;background:#121a26;color:#d9e1ec}.stButton>button:hover{border-color:#536b91;color:white}div[data-testid="stExpander"]{border:1px solid #253043;border-radius:12px;background:#101721}hr{border-color:#202a38}.footer-note{color:#66758a;font-size:11px;text-align:center;padding-top:16px}
</style>""",unsafe_allow_html=True)

with st.sidebar:
    st.markdown("<div class='brand'><div class='brand-mark'>🛡️</div><div><div class='brand-name'>NexaDesk</div><div class='brand-sub'>AI IT Operations Assistant</div></div></div>",unsafe_allow_html=True)
    st.divider(); st.markdown('<div class="sidebar-title">System status</div>',unsafe_allow_html=True)
    st.markdown('<div class="status"><span class="dot"></span> Local agent online</div>',unsafe_allow_html=True)
    st.write(f"**LLM**  `{OLLAMA_MODEL}`"); st.write(f"**Knowledge base**  `{'Ready' if rag_ready() else 'Not indexed'}`"); st.write(f"**Documents**  `{knowledge_count()}`"); st.write("**Diagnostics**  `6 read-only tools`"); st.write("**Memory**  `SQLite`")
    st.divider(); st.markdown('<div class="sidebar-title">Agent capabilities</div>',unsafe_allow_html=True)
    for text in ["Grounded knowledge retrieval","Conditional tool selection","Network diagnostics","System health checks","Disk and memory inspection","Persistent conversation history"]: st.markdown(f"<div class='sidebar-small'>● {text}</div>",unsafe_allow_html=True)
    st.divider()
    if st.button("＋ New support session",use_container_width=True): st.session_state.sid=str(uuid.uuid4());st.session_state.messages=[];st.session_state.tool_events=[];st.rerun()
    if st.button("🗑 Clear current session",use_container_width=True): clear(st.session_state.sid);st.session_state.messages=[];st.session_state.tool_events=[];st.rerun()
    st.markdown('<div class="footer-note">Safe by design · No arbitrary shell access</div>',unsafe_allow_html=True)

left,right=st.columns([4.5,1.2])
with left: st.markdown('<div class="hero-title">AI IT Helpdesk</div>',unsafe_allow_html=True);st.markdown('<div class="hero-sub">A grounded support agent that investigates issues instead of guessing.</div>',unsafe_allow_html=True)
with right: st.markdown('<div style="text-align:right;padding-top:10px"><span class="status"><span class="dot"></span> Ready</span></div>',unsafe_allow_html=True)
st.write("")
c1,c2,c3,c4=st.columns(4)
metrics=[(c1,"Agent runtime","LangGraph","Stateful tool workflow"),(c2,"Knowledge","ChromaDB",f"{knowledge_count()} source documents"),(c3,"Model","Ollama",OLLAMA_MODEL),(c4,"Memory","SQLite","Persistent session history")]
for col,label,value,note in metrics:
    with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)
st.write("")
tab_chat,tab_diagnostics,tab_knowledge=st.tabs(["💬 Support desk","🔧 Diagnostics","📚 Knowledge base"])

with tab_chat:
    if not st.session_state.messages:
        st.markdown('<div class="section-title">Start a diagnosis</div>',unsafe_allow_html=True)
        q1,q2,q3=st.columns(3)
        with q1: st.markdown('<div class="quick"><strong>🌐 Network issue</strong><span>“Wi-Fi is connected but internet is not working.”</span></div>',unsafe_allow_html=True)
        with q2: st.markdown('<div class="quick"><strong>💻 System check</strong><span>“Check my system information.”</span></div>',unsafe_allow_html=True)
        with q3: st.markdown('<div class="quick"><strong>💾 Storage issue</strong><span>“Is my disk space running low?”</span></div>',unsafe_allow_html=True)
        st.write("")
    for m in st.session_state.messages:
        if isinstance(m,HumanMessage):
            with st.chat_message("user",avatar="👤"): st.markdown(m.content)
        elif isinstance(m,AIMessage) and m.content:
            with st.chat_message("assistant",avatar="🛡️"): st.markdown(m.content)
    query=st.chat_input("Describe the IT problem you want me to investigate…")
    if query:
        st.session_state.messages.append(HumanMessage(content=query));save(st.session_state.sid,"user",query)
        with st.chat_message("user",avatar="👤"): st.markdown(query)
        with st.chat_message("assistant",avatar="🛡️"):
            progress=st.empty();progress.markdown("**Investigating your issue…**");started=datetime.now()
            try:
                result=graph.invoke({"messages":st.session_state.messages});st.session_state.last_latency=(datetime.now()-started).total_seconds();msgs=result["messages"];new_msgs=msgs[len(st.session_state.messages):];answer="";events=[]
                for m in new_msgs:
                    if isinstance(m,ToolMessage): events.append((m.name or "tool",m.content))
                    elif isinstance(m,AIMessage) and m.content: answer=m.content
                if not answer: answer=next((m.content for m in reversed(msgs) if isinstance(m,AIMessage) and m.content),"No answer generated.")
                progress.empty();st.markdown(answer);st.session_state.messages.append(AIMessage(content=answer));save(st.session_state.sid,"assistant",answer);st.session_state.tool_events=events
                if events:
                    with st.expander(f"🔧 Investigation trace · {len(events)} action(s)",expanded=False):
                        for name,output in events:
                            st.markdown(f"**{icon_for(name)} {display_name(name)}**")
                            try: st.json(json.loads(output))
                            except Exception: st.code(output[:5000])
            except Exception as exc:
                progress.empty();st.error("The agent could not complete the investigation.");st.caption("Check that Ollama is running and the configured model is available.")
                with st.expander("Technical details"): st.exception(exc)

with tab_diagnostics:
    st.markdown('<div class="section-title">Latest agent investigation</div>',unsafe_allow_html=True)
    if st.session_state.last_latency is not None: st.caption(f"Last response time: {st.session_state.last_latency:.2f}s")
    if not st.session_state.tool_events: st.info("No diagnostic actions have been recorded in this session yet. Ask the agent to diagnose a problem.")
    else:
        for name,output in st.session_state.tool_events:
            st.markdown(f"### {icon_for(name)} {display_name(name)}")
            try: st.json(json.loads(output))
            except Exception: st.code(output[:5000])

with tab_knowledge:
    st.markdown('<div class="section-title">Trusted IT knowledge sources</div>',unsafe_allow_html=True);st.caption("These Markdown sources are indexed into ChromaDB and can be retrieved by the agent.")
    docs=sorted(KNOWLEDGE_DIR.rglob("*.md")) if KNOWLEDGE_DIR.exists() else []
    if not docs: st.warning("No knowledge documents found.")
    else:
        for p in docs:
            rel=p.relative_to(KNOWLEDGE_DIR)
            with st.expander(f"📄 {rel}"): st.markdown(p.read_text(encoding="utf-8"))
st.divider();st.markdown('<div class="footer-note">NexaDesk · Agentic AI · RAG · Safe diagnostics · Local-first architecture</div>',unsafe_allow_html=True)
