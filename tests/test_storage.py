from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nb_auto.storage import download_urls, init_db, slugify, upsert_task


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "tasks.sqlite3"


# ---------------------------------------------------------------------------
# init_db
# ---------------------------------------------------------------------------


class TestInitDb:
    def test_creates_tasks_table(self, db_path: Path) -> None:
        init_db(db_path)
        with sqlite3.connect(db_path) as db:
            tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        assert "tasks" in tables

    def test_idempotent(self, db_path: Path) -> None:
        init_db(db_path)
        init_db(db_path)

    def test_creates_parent_directory(self, tmp_path: Path) -> None:
        deep = tmp_path / "a" / "b" / "tasks.sqlite3"
        init_db(deep)
        assert deep.exists()

    def test_table_has_expected_columns(self, db_path: Path) -> None:
        init_db(db_path)
        with sqlite3.connect(db_path) as db:
            cols = {row[1] for row in db.execute("PRAGMA table_info(tasks)").fetchall()}
        assert cols >= {"task_id", "model", "state", "prompt", "response_json", "created_at", "updated_at"}


# ---------------------------------------------------------------------------
# upsert_task
# ---------------------------------------------------------------------------


class TestUpsertTask:
    def test_inserts_row(self, db_path: Path) -> None:
        upsert_task(db_path, "t1", prompt="hello")
        with sqlite3.connect(db_path) as db:
            row = db.execute("SELECT task_id, prompt FROM tasks WHERE task_id='t1'").fetchone()
        assert row == ("t1", "hello")

    def test_default_state_is_created(self, db_path: Path) -> None:
        upsert_task(db_path, "t1")
        with sqlite3.connect(db_path) as db:
            state = db.execute("SELECT state FROM tasks WHERE task_id='t1'").fetchone()[0]
        assert state == "created"

    def test_default_model_is_nano_banana_pro(self, db_path: Path) -> None:
        upsert_task(db_path, "t1")
        with sqlite3.connect(db_path) as db:
            model = db.execute("SELECT model FROM tasks WHERE task_id='t1'").fetchone()[0]
        assert model == "nano-banana-pro"

    def test_updates_state_on_conflict(self, db_path: Path) -> None:
        upsert_task(db_path, "t1", state="created")
        upsert_task(db_path, "t1", state="success")
        with sqlite3.connect(db_path) as db:
            state = db.execute("SELECT state FROM tasks WHERE task_id='t1'").fetchone()[0]
        assert state == "success"

    def test_stores_response_json(self, db_path: Path) -> None:
        upsert_task(db_path, "t1", response={"code": 200, "data": {"taskId": "t1"}})
        with sqlite3.connect(db_path) as db:
            raw = db.execute("SELECT response_json FROM tasks WHERE task_id='t1'").fetchone()[0]
        assert json.loads(raw) == {"code": 200, "data": {"taskId": "t1"}}

    def test_empty_response_stored_as_empty_object(self, db_path: Path) -> None:
        upsert_task(db_path, "t1")
        with sqlite3.connect(db_path) as db:
            raw = db.execute("SELECT response_json FROM tasks WHERE task_id='t1'").fetchone()[0]
        assert json.loads(raw) == {}

    def test_updates_response_json_on_conflict(self, db_path: Path) -> None:
        upsert_task(db_path, "t1", response={"code": 200})
        upsert_task(db_path, "t1", response={"code": 200, "data": {"state": "success"}})
        with sqlite3.connect(db_path) as db:
            raw = db.execute("SELECT response_json FROM tasks WHERE task_id='t1'").fetchone()[0]
        assert json.loads(raw)["data"]["state"] == "success"


# ---------------------------------------------------------------------------
# slugify
# ---------------------------------------------------------------------------


class TestSlugify:
    def test_basic_lowercase(self) -> None:
        assert slugify("Hello World") == "hello-world"

    def test_special_chars_replaced(self) -> None:
        assert slugify("foo/bar:baz!") == "foo-bar-baz"

    def test_empty_string_uses_fallback(self) -> None:
        assert slugify("") == "image"

    def test_whitespace_only_uses_fallback(self) -> None:
        assert slugify("   ") == "image"

    def test_custom_fallback(self) -> None:
        assert slugify("", fallback="file") == "file"

    def test_strips_leading_trailing_hyphens(self) -> None:
        assert slugify("/hello/") == "hello"

    def test_truncates_at_80_chars(self) -> None:
        result = slugify("a" * 200)
        assert len(result) == 80

    def test_preserves_dots_and_hyphens(self) -> None:
        assert slugify("file-name.v2") == "file-name.v2"

    def test_consecutive_specials_collapse_to_one_hyphen(self) -> None:
        result = slugify("foo!!!bar")
        assert result == "foo-bar"


# ---------------------------------------------------------------------------
# download_urls
# ---------------------------------------------------------------------------


def _mock_stream_response(content: bytes = b"img") -> MagicMock:
    resp = MagicMock()
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    resp.raise_for_status.return_value = None
    resp.iter_content.return_value = [content] if content else []
    return resp


class TestDownloadUrls:
    def test_downloads_file_content(self, tmp_path: Path) -> None:
        with patch("nb_auto.storage.requests.get", return_value=_mock_stream_response(b"pixel")):
            paths = download_urls(["https://cdn.kie.ai/test.png"], tmp_path)
        assert len(paths) == 1
        assert paths[0].read_bytes() == b"pixel"

    def test_creates_output_directory(self, tmp_path: Path) -> None:
        new_dir = tmp_path / "sub" / "dir"
        with patch("nb_auto.storage.requests.get", return_value=_mock_stream_response()):
            download_urls(["https://cdn.kie.ai/test.png"], new_dir)
        assert new_dir.is_dir()

    def test_extension_taken_from_url(self, tmp_path: Path) -> None:
        with patch("nb_auto.storage.requests.get", return_value=_mock_stream_response()):
            paths = download_urls(["https://cdn.kie.ai/output.jpg"], tmp_path)
        assert paths[0].suffix == ".jpg"

    def test_falls_back_to_png_when_no_extension(self, tmp_path: Path) -> None:
        with patch("nb_auto.storage.requests.get", return_value=_mock_stream_response()):
            paths = download_urls(["https://cdn.kie.ai/output"], tmp_path)
        assert paths[0].suffix == ".png"

    def test_returns_path_objects(self, tmp_path: Path) -> None:
        with patch("nb_auto.storage.requests.get", return_value=_mock_stream_response()):
            paths = download_urls(["https://cdn.kie.ai/img.png"], tmp_path)
        assert isinstance(paths[0], Path)

    def test_multiple_urls_produce_multiple_files(self, tmp_path: Path) -> None:
        with patch("nb_auto.storage.requests.get", return_value=_mock_stream_response()):
            paths = download_urls(
                ["https://cdn.kie.ai/a.png", "https://cdn.kie.ai/b.png"],
                tmp_path,
            )
        assert len(paths) == 2
        assert paths[0] != paths[1]

    def test_empty_url_list_returns_empty(self, tmp_path: Path) -> None:
        paths = download_urls([], tmp_path)
        assert paths == []

    def test_prefix_used_in_filename(self, tmp_path: Path) -> None:
        with patch("nb_auto.storage.requests.get", return_value=_mock_stream_response()):
            paths = download_urls(["https://cdn.kie.ai/img.png"], tmp_path, prefix="task-abc")
        assert "task-abc" in paths[0].name
