import sqlite3
from app.config import SQLITE_DB
from langchain_core.messages import HumanMessage,AIMessage

def init():
    with sqlite3.connect(SQLITE_DB) as c:c.execute('CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,session TEXT,role TEXT,content TEXT,created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
def save(s,r,cnt):
    init()
    with sqlite3.connect(SQLITE_DB) as c:c.execute('INSERT INTO messages(session,role,content) VALUES(?,?,?)',(s,r,cnt));c.commit()
def load(s,limit=30):
    init()
    with sqlite3.connect(SQLITE_DB) as c: rows=c.execute('SELECT role,content FROM messages WHERE session=? ORDER BY id DESC LIMIT ?',(s,limit)).fetchall()[::-1]
    return [HumanMessage(content=x[1]) if x[0]=='user' else AIMessage(content=x[1]) for x in rows]
def clear(s):
    init()
    with sqlite3.connect(SQLITE_DB) as c:c.execute('DELETE FROM messages WHERE session=?',(s,));c.commit()
