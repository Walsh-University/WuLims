import uuid


def test_request_id_header_present(client):
    response = client.get("/")

    assert "X-Request-ID" in response
    assert response["X-Request-ID"] != ""


def test_request_id_is_valid_uuid(client):
    response = client.get("/")

    request_id = response["X-Request-ID"]

    uuid_obj = uuid.UUID(request_id)
    assert str(uuid_obj) == request_id


def test_request_id_is_unique_per_request(client):
    response1 = client.get("/")
    response2 = client.get("/")

    assert response1["X-Request-ID"] != response2["X-Request-ID"]
