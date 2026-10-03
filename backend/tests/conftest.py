import base64
import io
import os
import tempfile

# Use a throwaway database for tests. This must happen BEFORE the app is imported.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["USE_MONGOMOCK"] = "true"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
    os.unlink(_tmp.name)


def make_photo(top_rgb, bottom_rgb) -> str:
    """A fake 300x400 photo: the top guide box is one colour, the bottom guide box another."""
    img = Image.new("RGB", (300, 400), (128, 128, 128))
    draw = ImageDraw.Draw(img)
    draw.rectangle([84, 64, 216, 168], fill=top_rgb)       # inside TOP_BOX
    draw.rectangle([84, 208, 216, 340], fill=bottom_rgb)   # inside BOTTOM_BOX
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


@pytest.fixture()
def auth_headers(client):
    """Register a fresh user and return its Authorization header."""
    import uuid
    name = "user_" + uuid.uuid4().hex[:8]
    res = client.post("/api/auth/register", json={"username": name, "password": "secret123", "display_name": "Test"})
    assert res.status_code == 201
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
