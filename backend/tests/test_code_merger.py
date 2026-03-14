from app.services.code_merger import CodeMerger, Modification


def test_merge_ts_project_updates_and_deletes_files():
    merger = CodeMerger()
    original = """// filename: src/main.ts
import './styles.css';
console.log('old');

// filename: src/styles.css
body { color: red; }

// filename: src/obsolete.ts
export const legacy = true;
"""

    modifications = [
        Modification(type="file", target="src/main.ts", new_code="import './styles.css';\nconsole.log('new');"),
        Modification(type="file", target="src/game.ts", new_code="export class Game {}"),
        Modification(type="delete_file", target="src/obsolete.ts", new_code=""),
    ]

    result = merger.merge_ts_project(original, modifications)

    assert result.applied == 3
    assert "// filename: src/main.ts\nimport './styles.css';\nconsole.log('new');" in result.code
    assert "// filename: src/game.ts\nexport class Game {}" in result.code
    assert "src/obsolete.ts" not in result.code


def test_parse_modifications_supports_ts_file_blocks():
    merger = CodeMerger()
    response = """分析说明

<<<FILE: src/main.ts>>>
import './styles.css';
console.log('hello');
<<<END_FILE>>>

<<<DELETE_FILE: src/unused.ts>>>
<<<END_FILE>>>
"""

    modifications = merger.parse_modifications(response)

    assert [item.type for item in modifications] == ["file", "delete_file"]
    assert modifications[0].target == "src/main.ts"
    assert "console.log('hello');" in modifications[0].new_code
    assert modifications[1].target == "src/unused.ts"
