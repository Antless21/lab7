import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.parametrize("task", ["sqlite", "orm"])
def test_local_demo(task, tmp_path):
    result = subprocess.run(
        [sys.executable, "main.py", task, "--data-dir", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert "Мовчан Александр Дмитриевич" in result.stdout
    assert '"age": 21' in result.stdout


@pytest.mark.parametrize("task", ["postgres", "all"])
def test_postgres_requires_dsn(task, tmp_path):
    env = {key: value for key, value in os.environ.items() if key != "POSTGRES_DSN"}
    result = subprocess.run(
        [sys.executable, "main.py", task, "--data-dir", str(tmp_path)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    assert result.returncode == 2
    assert "POSTGRES_DSN" in result.stderr
    assert list(tmp_path.iterdir()) == []
