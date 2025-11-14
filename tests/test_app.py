def test_get_home(web_client):
    response = web_client.get("/")
    assert response.status_code == 200
    assert "<h2>Your Messages</h2>" in response.data.decode("utf-8")
    assert "<form action=" in response.data.decode("utf-8")
    