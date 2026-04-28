from app import create_app


def test_app_boots_and_registers_health_route():
    app = create_app("testing")
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/v1/health" in rules
    assert "/api/v1/auth/login" in rules
    assert "/api/v1/admin/users" in rules


def test_app_serves_built_frontend(tmp_path):
    dist_dir = tmp_path / "dist"
    assets_dir = dist_dir / "assets"
    assets_dir.mkdir(parents=True)
    (dist_dir / "index.html").write_text('<div id="root"></div>', encoding="utf-8")
    (assets_dir / "app.js").write_text("console.log('ok')", encoding="utf-8")

    app = create_app("testing", {"FRONTEND_DIST_DIR": str(dist_dir)})
    client = app.test_client()

    assert client.get("/").data == b'<div id="root"></div>'
    assert client.get("/workspace").data == b'<div id="root"></div>'
    assert client.get("/assets/app.js").data == b"console.log('ok')"
    assert client.get("/api/v1/missing").status_code == 404
