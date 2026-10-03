import uuid

from tests.conftest import make_photo

TOP_BOX = [0.28, 0.16, 0.72, 0.42]
BOTTOM_BOX = [0.28, 0.52, 0.72, 0.85]


def register(client, username=None, password="secret123"):
    username = username or "user_" + uuid.uuid4().hex[:8]
    res = client.post("/api/auth/register", json={"username": username, "password": password, "display_name": "Asha"})
    return username, res


def test_health(client):
    assert client.get("/api/health").json() == {"ok": True}


def test_register_login_and_me(client):
    username, res = register(client)
    assert res.status_code == 201
    token = res.json()["access_token"]
    assert "password" not in res.text

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200 and me.json()["username"] == username

    login = client.post("/api/auth/login", json={"username": username.upper(), "password": "secret123"})
    assert login.status_code == 200  # usernames are case-insensitive


def test_wrong_password_and_unknown_user_get_same_error(client):
    username, _ = register(client)
    bad_pw = client.post("/api/auth/login", json={"username": username, "password": "wrong-password"})
    unknown = client.post("/api/auth/login", json={"username": "nobody_here", "password": "whatever1"})
    assert bad_pw.status_code == unknown.status_code == 401
    assert bad_pw.json()["detail"] == unknown.json()["detail"]


def test_duplicate_username_rejected(client):
    username, _ = register(client)
    _, again = register(client, username=username)
    assert again.status_code == 409


def test_password_rules(client):
    _, short = register(client, password="123")
    assert short.status_code == 422


def test_password_is_stored_hashed(client):
    from app import models
    from app.database import SessionLocal

    username, _ = register(client, password="my-secret-pw")
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == username).first()
        assert user.password_hash != "my-secret-pw"
        assert user.password_hash.startswith("$2")  # bcrypt
    finally:
        db.close()


def test_routes_need_a_token(client):
    for path in ("/api/auth/me", "/api/preferences", "/api/history"):
        assert client.get(path).status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.token"}).status_code == 401


def test_preferences_roundtrip_and_validation(client, auth_headers):
    body = {"style_goal": "balance", "favorite_colors": "", "preferred_occasion": "festival", "skin_tone": "dusky"}
    assert client.put("/api/preferences", json=body, headers=auth_headers).status_code == 200
    assert client.get("/api/preferences", headers=auth_headers).json()["skin_tone"] == "dusky"

    bad = {**body, "skin_tone": "purple"}
    assert client.put("/api/preferences", json=bad, headers=auth_headers).status_code == 422


def test_analyze_full_flow(client, auth_headers):
    prefs = {"style_goal": "balance", "favorite_colors": "", "preferred_occasion": "office", "skin_tone": "wheatish"}
    client.put("/api/preferences", json=prefs, headers=auth_headers)

    photo = make_photo(top_rgb=(200, 30, 30), bottom_rgb=(20, 30, 90))  # red top, navy bottom
    res = client.post("/api/analyze", headers=auth_headers,
                      json={"image_base64": photo, "top_box": TOP_BOX, "bottom_box": BOTTOM_BOX})
    assert res.status_code == 200
    data = res.json()
    assert data["top_name"] == "red" and data["bottom_name"] == "navy"
    assert data["verdict"] == "good"
    assert "red" in data["summary"] and "navy" in data["summary"]
    assert data["accessories"] and data["footwear"] and data["skin_advice"] and data["tips"]

    history = client.get("/api/history", headers=auth_headers).json()
    assert len(history) == 1 and history[0]["id"] == data["check_id"]


def test_history_is_private_per_user(client, auth_headers):
    photo = make_photo((200, 30, 30), (20, 30, 90))
    client.post("/api/analyze", headers=auth_headers,
                json={"image_base64": photo, "top_box": TOP_BOX, "bottom_box": BOTTOM_BOX})

    _, other = register(client)
    other_headers = {"Authorization": f"Bearer {other.json()['access_token']}"}
    assert client.get("/api/history", headers=other_headers).json() == []


def test_analyze_rejects_bad_input(client, auth_headers):
    photo = make_photo((200, 30, 30), (20, 30, 90))
    bad_image = client.post("/api/analyze", headers=auth_headers,
                            json={"image_base64": "data:image/jpeg;base64,AAAA", "top_box": TOP_BOX, "bottom_box": BOTTOM_BOX})
    assert bad_image.status_code == 400

    bad_box = client.post("/api/analyze", headers=auth_headers,
                          json={"image_base64": photo, "top_box": [0.8, 0.1, 0.2, 0.4], "bottom_box": BOTTOM_BOX})
    assert bad_box.status_code == 422

    no_token = client.post("/api/analyze", json={"image_base64": photo, "top_box": TOP_BOX, "bottom_box": BOTTOM_BOX})
    assert no_token.status_code == 401


def test_tips_are_public(client):
    res = client.get("/api/tips", params={"goal": "relaxed"})
    assert res.status_code == 200 and len(res.json()) == 3
