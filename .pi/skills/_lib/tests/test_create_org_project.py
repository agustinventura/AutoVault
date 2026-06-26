"""Tests de integración de create_org.py y create_project.py."""

import json

from conftest import skill_script, run_script


def run(name, vault, *extra):
    return run_script(skill_script(name), "--vault-root", str(vault), *extra)


# ── create-org ──────────────────────────────────────────────────────────────

class TestCreateOrg:
    def test_creates_org_dir_and_note(self, vault):
        r = run("create-org", vault, "--name", "Mango")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True
        assert (vault / "Mango").is_dir()
        assert (vault / "Mango" / "Mango.md").exists()

    def test_frontmatter_type_is_org(self, vault):
        run("create-org", vault, "--name", "Mango")
        from vault import markdown as md
        content = (vault / "Mango" / "Mango.md").read_text(encoding="utf-8")
        assert md.get_field(content, "type") == "org"
        assert md.get_field(content, "name") == "Mango"

    def test_idempotent_returns_ok(self, vault):
        run("create-org", vault, "--name", "Mango")
        r = run("create-org", vault, "--name", "Mango")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True

    def test_sanitizes_name_in_file(self, vault):
        r = run("create-org", vault, "--name", "My:Org")
        assert r.returncode == 0
        assert (vault / "My-Org").is_dir()


# ── create-project ───────────────────────────────────────────────────────────

class TestCreateProject:
    def test_creates_project_dir_and_note(self, vault):
        run("create-org", vault, "--name", "Mango")
        r = run("create-project", vault,
                "--org", "Mango", "--name", "Kondo",
                "--description", "Gestión de listados")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True
        assert (vault / "Mango" / "Proyectos" / "Kondo" / "Kondo.md").exists()

    def test_frontmatter_fields(self, vault):
        run("create-org", vault, "--name", "Mango")
        run("create-project", vault,
            "--org", "Mango", "--name", "Kondo", "--description", "Desc")
        from vault import markdown as md
        content = (vault / "Mango" / "Proyectos" / "Kondo" / "Kondo.md").read_text(encoding="utf-8")
        assert md.get_field(content, "type") == "project"
        assert md.get_field(content, "org") == "Mango"
        assert "Kondo" in md.get_field(content, "tags")

    def test_fails_if_org_missing(self, vault):
        r = run("create-project", vault,
                "--org", "NoExiste", "--name", "Kondo", "--description", "x")
        assert r.returncode != 0
        data = json.loads(r.stdout)
        assert data["ok"] is False
        assert "ORG_NOT_FOUND" in data["code"]

    def test_idempotent(self, vault):
        run("create-org", vault, "--name", "Mango")
        run("create-project", vault,
            "--org", "Mango", "--name", "Kondo", "--description", "x")
        r = run("create-project", vault,
                "--org", "Mango", "--name", "Kondo", "--description", "x")
        assert r.returncode == 0
        assert json.loads(r.stdout)["ok"] is True
