import logging


def form(**over):
    d = {"name": "Влад", "email": "a@b.com", "phone": "+380501234567",
         "topic": "question", "message": "Це тестове повідомлення"}
    d.update(over)
    return d


def test_get_contact(client):
    assert client.get("/contact").status_code == 200


def test_valid_post_redirects_and_flashes(client, caplog):
    with caplog.at_level(logging.INFO, logger="contacts"):
        r = client.post("/contact", data=form())
    assert r.status_code == 302 and r.headers["Location"].endswith("/contact")
    assert "a@b.com" in caplog.text
    assert "alert-success" in client.get("/contact").get_data(as_text=True)


def test_invalid_email(client):
    r = client.post("/contact", data=form(email="nope"))
    html = r.get_data(as_text=True)
    assert r.status_code == 200 and "Невірний формат email" in html and "alert-danger" in html


def test_topic_required(client):
    r = client.post("/contact", data=form(topic="", message="short"))
    assert "Оберіть тему" in r.get_data(as_text=True)


def test_phone_optional(client):
    assert client.post("/contact", data=form(phone="")).status_code == 302


def test_csrf_enforced(client):
    from app import app
    app.config["WTF_CSRF_ENABLED"] = True
    r = client.post("/contact", data=form())
    assert r.status_code == 200 and "alert-danger" in r.get_data(as_text=True)
