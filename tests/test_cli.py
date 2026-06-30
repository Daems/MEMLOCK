from __future__ import annotations

import argparse
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from nb_auto.cli import cmd_submit, cmd_submit_yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _submit_args(**overrides) -> argparse.Namespace:
    base = dict(
        prompt="test prompt",
        image_input=None,
        aspect_ratio="1:1",
        resolution="1K",
        output_format="png",
        callback_url=None,
        download=False,
        dry_run=False,
    )
    base.update(overrides)
    return argparse.Namespace(**base)


def _yaml_args(**overrides) -> argparse.Namespace:
    base = dict(download=False, dry_run=False)
    base.update(overrides)
    return argparse.Namespace(**base)


def _mock_build_client(task_id: str = "task-xyz"):
    mock_client = MagicMock()
    mock_settings = MagicMock()
    mock_settings.callback_url = None
    mock_settings.db_path = Path("/tmp/nb_test.sqlite3")
    mock_settings.output_dir = Path("/tmp/nb_outputs")
    mock_settings.default_aspect_ratio = "1:1"
    mock_settings.default_resolution = "1K"
    mock_settings.default_output_format = "png"
    mock_client.create_nano_banana_pro_task.return_value = {
        "code": 200,
        "data": {"taskId": task_id},
    }
    mock_client.build_task_payload.side_effect = lambda **kwargs: {
        "model": "nano-banana-pro",
        "input": {k: v for k, v in kwargs.items() if k != "callback_url"},
        **({"callBackUrl": kwargs["callback_url"]} if kwargs.get("callback_url") else {}),
    }
    return mock_client, mock_settings


# ---------------------------------------------------------------------------
# submit --dry-run
# ---------------------------------------------------------------------------


class TestSubmitDryRun:
    def test_prints_valid_json_payload(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        cmd_submit(_submit_args(dry_run=True))
        out = capsys.readouterr().out
        payload = json.loads(out)
        assert payload["model"] == "nano-banana-pro"
        assert payload["input"]["prompt"] == "test prompt"

    def test_does_not_call_api(self, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        with patch("nb_auto.kie_client.requests.post") as mock_post:
            cmd_submit(_submit_args(dry_run=True))
        mock_post.assert_not_called()

    def test_stable_output_across_calls(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        results = []
        for _ in range(3):
            cmd_submit(_submit_args(prompt="stability check", dry_run=True))
            results.append(capsys.readouterr().out.strip())
        assert len(set(results)) == 1

    def test_output_is_sorted_json(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        cmd_submit(_submit_args(dry_run=True))
        out = capsys.readouterr().out.strip()
        assert out == json.dumps(json.loads(out), indent=2, sort_keys=True, ensure_ascii=False)

    def test_includes_custom_aspect_ratio_and_resolution(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        cmd_submit(_submit_args(dry_run=True, aspect_ratio="16:9", resolution="2K", output_format="jpg"))
        payload = json.loads(capsys.readouterr().out)
        assert payload["input"]["aspect_ratio"] == "16:9"
        assert payload["input"]["resolution"] == "2K"
        assert payload["input"]["output_format"] == "jpg"

    def test_includes_callback_url_when_provided(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        cmd_submit(_submit_args(dry_run=True, callback_url="https://example.com/cb"))
        payload = json.loads(capsys.readouterr().out)
        assert payload["callBackUrl"] == "https://example.com/cb"

    def test_callback_url_absent_when_not_set(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        cmd_submit(_submit_args(dry_run=True))
        payload = json.loads(capsys.readouterr().out)
        assert "callBackUrl" not in payload

    def test_invalid_prompt_raises_before_print(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            cmd_submit(_submit_args(prompt="", dry_run=True))
        assert capsys.readouterr().out == ""


# ---------------------------------------------------------------------------
# submit-yaml --dry-run
# ---------------------------------------------------------------------------


class TestSubmitYamlDryRun:
    def test_prints_payload_from_yaml(self, tmp_path, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        job = tmp_path / "job.yaml"
        job.write_text("prompt: 'cheesecake ad'\naspect_ratio: '2:3'\nresolution: '2K'\noutput_format: png\n")
        cmd_submit_yaml(_yaml_args(path=str(job), dry_run=True))
        payload = json.loads(capsys.readouterr().out)
        assert payload["input"]["prompt"] == "cheesecake ad"
        assert payload["input"]["aspect_ratio"] == "2:3"
        assert payload["input"]["resolution"] == "2K"

    def test_does_not_call_api(self, tmp_path, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        job = tmp_path / "job.yaml"
        job.write_text("prompt: 'test'\n")
        with patch("nb_auto.kie_client.requests.post") as mock_post:
            cmd_submit_yaml(_yaml_args(path=str(job), dry_run=True))
        mock_post.assert_not_called()

    def test_output_is_sorted_json(self, tmp_path, capsys, monkeypatch) -> None:
        monkeypatch.setenv("KIE_API_KEY", "test-key")
        job = tmp_path / "job.yaml"
        job.write_text("prompt: 'a'\n")
        cmd_submit_yaml(_yaml_args(path=str(job), dry_run=True))
        out = capsys.readouterr().out.strip()
        assert out == json.dumps(json.loads(out), indent=2, sort_keys=True, ensure_ascii=False)


# ---------------------------------------------------------------------------
# submit normal path (API mocked)
# ---------------------------------------------------------------------------


class TestSubmitNormal:
    def test_calls_create_task(self) -> None:
        mock_client, mock_settings = _mock_build_client()
        with patch("nb_auto.cli.build_client", return_value=(mock_client, mock_settings)):
            with patch("nb_auto.cli.upsert_task"):
                cmd_submit(_submit_args())
        mock_client.create_nano_banana_pro_task.assert_called_once()

    def test_prints_response_json(self, capsys) -> None:
        mock_client, mock_settings = _mock_build_client(task_id="task-abc")
        with patch("nb_auto.cli.build_client", return_value=(mock_client, mock_settings)):
            with patch("nb_auto.cli.upsert_task"):
                cmd_submit(_submit_args())
        out = json.loads(capsys.readouterr().out)
        assert out["data"]["taskId"] == "task-abc"

    def test_upserts_task_when_task_id_present(self) -> None:
        mock_client, mock_settings = _mock_build_client(task_id="task-abc")
        with patch("nb_auto.cli.build_client", return_value=(mock_client, mock_settings)):
            with patch("nb_auto.cli.upsert_task") as mock_upsert:
                cmd_submit(_submit_args())
        mock_upsert.assert_called_once()
        assert mock_upsert.call_args[0][1] == "task-abc"

    def test_no_upsert_when_no_task_id(self) -> None:
        mock_client, mock_settings = _mock_build_client()
        mock_client.create_nano_banana_pro_task.return_value = {"code": 200, "data": {}}
        with patch("nb_auto.cli.build_client", return_value=(mock_client, mock_settings)):
            with patch("nb_auto.cli.upsert_task") as mock_upsert:
                cmd_submit(_submit_args())
        mock_upsert.assert_not_called()
