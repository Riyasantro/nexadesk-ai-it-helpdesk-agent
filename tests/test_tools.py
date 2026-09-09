from app.tools import system_info,disk_space,memory_usage,dns_lookup,check_network
def test_system(): assert 'os' in system_info.invoke({})
def test_disk(): assert 'total_gb' in disk_space.invoke({'path':'/'})
def test_memory(): assert 'total_gb' in memory_usage.invoke({})
def test_dns(): assert 'domain' in dns_lookup.invoke({'domain':'example.com'})
def test_network(): assert 'interfaces' in check_network.invoke({})
