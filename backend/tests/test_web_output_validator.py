import shutil

import pytest

from app.services.ts_builder import TSCommandResult
from app.services.web_output_validator import WebOutputValidator


VALID_DOM_HTML = """<!DOCTYPE html>
<html>
<head>
  <meta charset=\"UTF-8\" />
  <style>.board { display: grid; grid-template-columns: repeat(8, 1fr); }</style>
</head>
<body>
  <div id=\"status\"></div>
  <button id=\"shuffleBtn\">Shuffle</button>
  <script>
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('shuffleBtn').addEventListener('click', () => {
      document.getElementById('status').textContent = 'ready';
    });
  });
  </script>
</body>
</html>"""


def test_validator_accepts_dom_interactive_without_canvas():
    validator = WebOutputValidator()

    result = validator.validate_html_output(VALID_DOM_HTML, stage="test", requirements="做一个三消棋盘网页")

    assert result.passed is True
    assert result.signals["profile"] == "dom-interactive"
    assert not any("Canvas" in error for error in result.errors)


def test_validator_reports_missing_dom_id_and_js_syntax_error():
    validator = WebOutputValidator()
    invalid_html = """<!DOCTYPE html>
<html>
<body>
  <button id=\"runBtn\">Run</button>
  <script>
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('missingPanel').textContent = 'x';
    const broken = ;
  });
  </script>
</body>
</html>"""

    result = validator.validate_html_output(invalid_html, stage="test", requirements="DOM 交互页")

    assert result.passed is False
    assert any("DOM id" in error for error in result.errors)
    syntax_errors = [error for error in result.errors if "JavaScript 语法检查失败" in error]
    assert syntax_errors
    assert any("SyntaxError" in error for error in syntax_errors)
    assert any("const broken = ;" in error for error in syntax_errors)


@pytest.mark.skipif(shutil.which("node") is None, reason="node is required for smoke test")
def test_minimal_dom_smoke_detects_runtime_bootstrap_error():
    validator = WebOutputValidator()
    broken_runtime_html = """<!DOCTYPE html>
<html>
<body>
  <button id=\"runBtn\">Run</button>
  <script>
  window.onload = () => {
    missingGlobal.doSomething();
  };
  </script>
</body>
</html>"""

    smoke = validator.run_minimal_dom_smoke_test(broken_runtime_html)

    assert smoke["passed"] is False
    assert "missingGlobal" in smoke.get("error", "")


def test_validate_ts_project_detects_placeholder_and_compile_failure(tmp_path, monkeypatch):
    validator = WebOutputValidator()
    project_dir = tmp_path / "ts-app"
    src_dir = project_dir / "src"
    src_dir.mkdir(parents=True)
    (src_dir / "main.ts").write_text(
        "const root = document.getElementById('app');\nroot!.textContent = '等待生成具体业务代码';\n",
        encoding="utf-8",
    )

    def fake_compile_check(_project_dir: str) -> TSCommandResult:
        return TSCommandResult(
            passed=False,
            command=["npm", "run", "typecheck"],
            stdout="",
            stderr="compile failed",
            returncode=1,
            errors=["src/main.ts:1: error TS2304: Cannot find name 'document'."],
            warnings=[],
        )

    monkeypatch.setattr("app.services.web_output_validator.ts_builder.compile_check", fake_compile_check)

    result = validator.validate_ts_project(str(project_dir), stage="pretest", requirements="做一个 TypeScript 页面")

    assert result.passed is False
    assert result.signals["has_main_entry"] is True
    assert any("占位" in error for error in result.errors)
    assert any("编译检查失败" in error for error in result.errors)


def test_validate_ts_project_flags_css_import_drift_and_missing_dom_anchor(tmp_path, monkeypatch):
    validator = WebOutputValidator()
    project_dir = tmp_path / "ts-app"
    src_dir = project_dir / "src"
    src_dir.mkdir(parents=True)

    (project_dir / "index.html").write_text(
        "<!DOCTYPE html><html><body><div id='app'></div></body></html>",
        encoding="utf-8",
    )
    (src_dir / "main.ts").write_text(
        "import './style.css';\n"
        "const canvas = document.getElementById('gameCanvas');\n"
        "if (!canvas) throw new Error('Canvas missing');\n",
        encoding="utf-8",
    )
    (src_dir / "styles.css").write_text("body { margin: 0; }", encoding="utf-8")

    def fake_compile_check(_project_dir: str) -> TSCommandResult:
        return TSCommandResult(
            passed=True,
            command=["npm", "run", "typecheck"],
            stdout="",
            stderr="",
            returncode=0,
            errors=[],
            warnings=[],
        )

    monkeypatch.setattr("app.services.web_output_validator.ts_builder.compile_check", fake_compile_check)

    result = validator.validate_ts_project(str(project_dir), stage="pretest", requirements="做一个 TypeScript 贪吃蛇游戏")

    assert result.passed is False
    assert result.signals["missing_dom_ids"] == ["gameCanvas"]
    assert result.signals["missing_css_imports"]
    assert any("gameCanvas" in error for error in result.errors)
    assert any("styles.css" in error for error in result.errors)
