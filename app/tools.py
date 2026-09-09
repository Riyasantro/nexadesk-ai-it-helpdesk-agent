import json, socket, subprocess, platform, shutil, os, psutil
from langchain_core.tools import tool

def cmd(args):
    try:
        p=subprocess.run(args,capture_output=True,text=True,timeout=6,check=False)
        return (p.stdout or p.stderr).strip()
    except Exception as e: return f'error: {e}'

@tool
def check_network()->str:
    """Inspect network interfaces and addresses. Read-only."""
    out=[]
    for name,addrs in psutil.net_if_addrs().items():
        s=psutil.net_if_stats().get(name)
        out.append({'name':name,'up':s.isup if s else None,'addresses':[a.address for a in addrs]})
    return json.dumps({'interfaces':out},indent=2)

@tool
def ping_host(host:str)->str:
    """Ping a hostname or IP for basic connectivity diagnostics. Read-only."""
    host=host.strip()
    if not host or len(host)>253 or any(c in host for c in ';&|`$()<>'): return json.dumps({'error':'invalid host'})
    return json.dumps({'host':host,'result':cmd(['ping','-c','2','-W','2',host])},indent=2)

@tool
def dns_lookup(domain:str)->str:
    """Resolve a domain with the local resolver. Read-only."""
    domain=domain.strip().rstrip('.')
    if not domain or len(domain)>253 or any(c in domain for c in ';&|`$()<>/'): return json.dumps({'error':'invalid domain'})
    try:
        ips=sorted({x[4][0] for x in socket.getaddrinfo(domain,443,type=socket.SOCK_STREAM)})
        return json.dumps({'domain':domain,'addresses':ips},indent=2)
    except Exception as e: return json.dumps({'domain':domain,'error':str(e)},indent=2)

@tool
def system_info()->str:
    """Return basic OS and hardware information. Read-only."""
    return json.dumps({'os':platform.system(),'release':platform.release(),'machine':platform.machine(),'processor':platform.processor(),'cpu_count':os.cpu_count(),'python':platform.python_version()},indent=2)

@tool
def disk_space(path:str='/')->str:
    """Inspect filesystem disk usage. Read-only."""
    try:
        t,u,f=shutil.disk_usage(path or '/')
        return json.dumps({'path':path,'total_gb':round(t/2**30,2),'used_gb':round(u/2**30,2),'free_gb':round(f/2**30,2),'used_percent':round(u/t*100,2)},indent=2)
    except Exception as e:return json.dumps({'error':str(e)})

@tool
def memory_usage()->str:
    """Inspect RAM usage. Read-only."""
    m=psutil.virtual_memory(); return json.dumps({'total_gb':round(m.total/2**30,2),'available_gb':round(m.available/2**30,2),'used_gb':round(m.used/2**30,2),'used_percent':m.percent},indent=2)
