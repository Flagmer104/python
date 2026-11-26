import io

from app.utils.repo import product_repo
from conftest import PNG, valid_data


def add(client, **over):
    return client.post("/product/add", data=valid_data(**over), follow_redirects=False)


def add_with_image(client, filename="a.png"):
    data = valid_data()
    data["image"] = (io.BytesIO(PNG), filename)
    return client.post("/product/add", data=data, content_type="multipart/form-data")


def test_list_empty(client):
    r = client.get("/product")
    assert r.status_code == 200
    assert "Товарів поки немає" in r.get_data(as_text=True)


def test_create_product_prg_and_fields(client):
    r = add(client)
    assert r.status_code == 302 and r.headers["Location"].endswith("/product/1")
    p = product_repo.get_by_id(1)
    assert p["name"] == "Laptop" and p["price"] == 1200.5 and p["quantity"] == 5
    assert p["created_at"] and p["image"] is None


def test_ids_are_unique_and_increment(client):
    add(client)
    add(client, name="Phone")
    assert [p["id"] for p in product_repo.get_all()] == [1, 2]


def test_flash_success_after_create(client):
    r = client.post("/product/add", data=valid_data(), follow_redirects=True)
    assert "додано" in r.get_data(as_text=True)


def test_validation_name_too_short(client):
    r = add(client, name="ab")
    assert r.status_code == 200
    assert "Мінімум 3 символи" in r.get_data(as_text=True)
    assert product_repo.get_all() == []


def test_validation_price_must_be_positive(client):
    for bad in ("0", "-5"):
        assert add(client, price=bad).status_code == 200
    assert product_repo.get_all() == []


def test_validation_price_two_decimals(client):
    r = add(client, price="1.999")
    assert r.status_code == 200 and product_repo.get_all() == []


def test_validation_quantity_negative(client):
    r = add(client, quantity="-1")
    assert r.status_code == 200 and product_repo.get_all() == []


def test_validation_invalid_category(client):
    assert add(client, category="bogus").status_code == 200
    assert product_repo.get_all() == []


def test_detail_and_not_found(client):
    add(client)
    assert client.get("/product/1").status_code == 200
    assert client.get("/product/99").status_code == 404


def test_edit_keeps_id_and_created_at(client):
    add(client)
    before = product_repo.get_by_id(1)
    r = client.post("/product/1/edit", data=valid_data(name="Laptop Pro", price="999"))
    assert r.status_code == 302
    after = product_repo.get_by_id(1)
    assert after["name"] == "Laptop Pro" and after["price"] == 999
    assert after["id"] == 1 and after["created_at"] == before["created_at"]


def test_edit_form_prefilled(client):
    add(client)
    html = client.get("/product/1/edit").get_data(as_text=True)
    assert 'value="Laptop"' in html


def test_edit_not_found(client):
    assert client.post("/product/42/edit", data=valid_data()).status_code == 404


def test_delete_post_only(client):
    add(client)
    assert client.get("/product/1/delete").status_code == 405
    r = client.post("/product/1/delete")
    assert r.status_code == 302
    assert product_repo.get_by_id(1) is None
    assert client.post("/product/1/delete").status_code == 404


def test_upload_image_saved_with_uuid_name(client):
    r = add_with_image(client, "my photo.png")
    assert r.status_code == 302
    img = product_repo.get_by_id(1)["image"]
    assert img.startswith("uploads/") and img.endswith(".png") and "photo" not in img
    assert img in client.get("/product/1").get_data(as_text=True)


def test_upload_rejects_wrong_extension(client):
    data = valid_data()
    data["image"] = (io.BytesIO(b"x"), "evil.exe")
    r = client.post("/product/add", data=data, content_type="multipart/form-data")
    assert r.status_code == 200 and product_repo.get_all() == []


def test_edit_keeps_old_image_when_not_replaced(client):
    add_with_image(client)
    old = product_repo.get_by_id(1)["image"]
    client.post("/product/1/edit", data=valid_data(name="Renamed"))
    assert product_repo.get_by_id(1)["image"] == old


def test_edit_replaces_image(client):
    add_with_image(client)
    old = product_repo.get_by_id(1)["image"]
    data2 = valid_data()
    data2["image"] = (io.BytesIO(PNG), "b.png")
    client.post("/product/1/edit", data=data2, content_type="multipart/form-data")
    assert product_repo.get_by_id(1)["image"] != old


def test_missing_image_placeholder(client):
    add(client)
    assert "Зображення відсутнє" in client.get("/product/1").get_data(as_text=True)
    assert "немає фото" in client.get("/product").get_data(as_text=True)


def test_too_large_upload_rejected(client):
    from app import app
    app.config["MAX_CONTENT_LENGTH"] = 1024
    try:
        data = valid_data()
        data["image"] = (io.BytesIO(b"0" * 5000), "big.png")
        r = client.post("/product/add", data=data, content_type="multipart/form-data")
        assert r.status_code == 413
    finally:
        app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024


def test_persistence_between_restarts(client, tmp_path):
    add(client)
    product_repo.init(str(tmp_path / "products.json"))  # «перезапуск»: повторне відкриття файлу
    assert product_repo.get_by_id(1)["name"] == "Laptop"
