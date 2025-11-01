"""
Teste da aplicação principal
"""
def test_root_endpoint(client):
    """Testa endpoint raiz"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AlugueisV5 API"
    assert data["version"] == "5.0.0"
    assert data["status"] == "running"


def test_health_check(client):
    """Testa endpoint de health check"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
