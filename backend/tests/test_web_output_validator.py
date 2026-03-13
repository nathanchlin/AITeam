import shutil

import pytest

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
    assert any("JavaScript 语法检查失败" in error for error in result.errors)


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
