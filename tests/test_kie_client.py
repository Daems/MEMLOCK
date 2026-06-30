from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from nb_auto.kie_client import KieClient


@pytest.fixture
def client() -> KieClient:
    return KieClient(api_key="test-key")


# ---------------------------------------------------------------------------
# build_task_payload — validation and payload shape
# ---------------------------------------------------------------------------


class TestBuildTaskPayload:
    def test_empty_prompt_raises(self, client: KieClient) -> None:
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            client.build_task_payload(prompt="")

    def test_whitespace_prompt_raises(self, client: KieClient) -> None:
        with pytest.raises(ValueError, match="prompt cannot be empty"):
            client.build_task_payload(prompt="   ")

    def test_invalid_aspect_ratio_raises(self, client: KieClient) -> None:
        with pytest.raises(ValueError, match="Unsupported aspect_ratio"):
            client.build_task_payload(prompt="p", aspect_ratio="bad")

    def test_invalid_resolution_raises(self, client: KieClient) -> None:
        with pytest.raises(ValueError, match="Unsupported resolution"):
            client.build_task_payload(prompt="p", resolution="8K")

    def test_invalid_output_format_raises(self, client: KieClient) -> None:
        with pytest.raises(ValueError, match="Unsupported output_format"):
            client.build_task_payload(prompt="p", output_format="gif")

    def test_valid_payload_structure(self, client: KieClient) -> None:
        payload = client.build_task_payload(prompt="hello")
        assert payload["model"] == "nano-banana-pro"
        assert payload["input"]["prompt"] == "hello"
        assert payload["input"]["aspect_ratio"] == "1:1"
        assert payload["input"]["resolution"] == "1K"
        assert payload["input"]["output_format"] == "png"
        assert payload["input"]["image_input"] == []

    def test_image_input_defaults_to_empty_list(self, client: KieClient) -> None:
        payload = client.build_task_payload(prompt="p")
        assert payload["input"]["image_input"] == []

    def test_image_input_passed_through(self, client: KieClient) -> None:
        payload = client.build_task_payload(prompt="p", image_input=["https://example.com/img.png"])
        assert payload["input"]["image_input"] == ["https://example.com/img.png"]

    def test_callback_url_excluded_when_none(self, client: KieClient) -> None:
        payload = client.build_task_payload(prompt="p")
        assert "callBackUrl" not in payload

    def test_callback_url_included_when_provided(self, client: KieClient) -> None:
        payload = client.build_task_payload(prompt="p", callback_url="https://example.com/cb")
        assert payload["callBackUrl"] == "https://example.com/cb"

    def test_all_valid_aspect_ratios_accepted(self, client: KieClient) -> None:
        for ratio in ("1:1", "2:3", "3:2", "16:9", "9:16", "21:9", "auto"):
            payload = client.build_task_payload(prompt="p", aspect_ratio=ratio)
            assert payload["input"]["aspect_ratio"] == ratio

    def test_all_valid_resolutions_accepted(self, client: KieClient) -> None:
        for res in ("1K", "2K", "4K"):
            payload = client.build_task_payload(prompt="p", resolution=res)
            assert payload["input"]["resolution"] == res


# ---------------------------------------------------------------------------
# create_nano_banana_pro_task — HTTP dispatch
# ---------------------------------------------------------------------------


class TestCreateTask:
    def _mock_ok_response(self, body: dict) -> MagicMock:
        resp = MagicMock()
        resp.ok = True
        resp.json.return_value = body
        return resp

    def test_posts_to_create_task_endpoint(self, client: KieClient) -> None:
        with patch("nb_auto.kie_client.requests.post", return_value=self._mock_ok_response({"code": 200, "data": {}})) as mock_post:
            client.create_nano_banana_pro_task(prompt="hello")
        url = mock_post.call_args[0][0]
        assert url == "https://api.kie.ai/api/v1/jobs/createTask"

    def test_sets_bearer_auth_header(self, client: KieClient) -> None:
        with patch("nb_auto.kie_client.requests.post", return_value=self._mock_ok_response({"code": 200, "data": {}})) as mock_post:
            client.create_nano_banana_pro_task(prompt="hello")
        headers = mock_post.call_args[1]["headers"]
        assert headers["Authorization"] == "Bearer test-key"

    def test_payload_forwarded_to_post(self, client: KieClient) -> None:
        with patch("nb_auto.kie_client.requests.post", return_value=self._mock_ok_response({"code": 200, "data": {}})) as mock_post:
            client.create_nano_banana_pro_task(prompt="a banana", resolution="2K")
        body = mock_post.call_args[1]["json"]
        assert body["model"] == "nano-banana-pro"
        assert body["input"]["prompt"] == "a banana"
        assert body["input"]["resolution"] == "2K"

    def test_validation_errors_surface_before_http(self, client: KieClient) -> None:
        with patch("nb_auto.kie_client.requests.post") as mock_post:
            with pytest.raises(ValueError):
                client.create_nano_banana_pro_task(prompt="")
        mock_post.assert_not_called()


# ---------------------------------------------------------------------------
# _decode_response — success and error paths
# ---------------------------------------------------------------------------


class TestDecodeResponse:
    def _resp(self, *, ok: bool = True, status: int = 200, body=None, json_error: bool = False) -> MagicMock:
        resp = MagicMock()
        resp.ok = ok
        resp.status_code = status
        if json_error:
            resp.json.side_effect = ValueError("not json")
        else:
            resp.json.return_value = body if body is not None else {}
        return resp

    def test_http_error_raises(self) -> None:
        resp = self._resp(ok=False, status=400, body={"msg": "bad"})
        with pytest.raises(RuntimeError, match="Kie API HTTP 400"):
            KieClient._decode_response(resp)

    def test_non_json_with_http_error_propagates_raise_for_status(self) -> None:
        resp = self._resp(json_error=True)
        resp.raise_for_status.side_effect = RuntimeError("HTTP 500")
        with pytest.raises(RuntimeError, match="HTTP 500"):
            KieClient._decode_response(resp)

    def test_non_json_without_http_error_raises_runtime_error(self) -> None:
        resp = self._resp(json_error=True)
        resp.raise_for_status.return_value = None
        with pytest.raises(RuntimeError, match="non-JSON"):
            KieClient._decode_response(resp)

    def test_api_error_code_with_error_msg_raises(self) -> None:
        resp = self._resp(body={"code": 400, "msg": "invalid request"})
        with pytest.raises(RuntimeError, match="Kie API error"):
            KieClient._decode_response(resp)

    def test_api_error_code_with_success_msg_does_not_raise(self) -> None:
        resp = self._resp(body={"code": 400, "msg": "success"})
        result = KieClient._decode_response(resp)
        assert result["code"] == 400

    def test_success_code_none(self) -> None:
        resp = self._resp(body={"code": None, "data": {"taskId": "t1"}})
        assert KieClient._decode_response(resp)["data"]["taskId"] == "t1"

    def test_success_code_200(self) -> None:
        resp = self._resp(body={"code": 200, "data": {}})
        assert KieClient._decode_response(resp)["code"] == 200

    def test_success_code_505_with_success_msg(self) -> None:
        resp = self._resp(body={"code": 505, "msg": "success", "data": {}})
        result = KieClient._decode_response(resp)
        assert result["code"] == 505

    def test_non_dict_body_returned_as_is(self) -> None:
        resp = self._resp(body=["item1", "item2"])
        result = KieClient._decode_response(resp)
        assert result == ["item1", "item2"]


# ---------------------------------------------------------------------------
# extract_result_urls
# ---------------------------------------------------------------------------


class TestExtractResultUrls:
    def test_empty_response_returns_empty(self) -> None:
        assert KieClient.extract_result_urls({}) == []

    def test_result_json_as_string(self) -> None:
        payload = {"data": {"resultJson": json.dumps({"resultUrls": ["https://cdn.kie.ai/img/a.png"]})}}
        assert KieClient.extract_result_urls(payload) == ["https://cdn.kie.ai/img/a.png"]

    def test_result_json_as_dict(self) -> None:
        payload = {"data": {"resultJson": {"resultUrls": ["https://cdn.kie.ai/img/a.png"]}}}
        assert KieClient.extract_result_urls(payload) == ["https://cdn.kie.ai/img/a.png"]

    def test_result_urls_fallback_key(self) -> None:
        payload = {"data": {"resultJson": {"result_urls": ["https://cdn.kie.ai/img/b.png"]}}}
        assert KieClient.extract_result_urls(payload) == ["https://cdn.kie.ai/img/b.png"]

    def test_urls_fallback_key(self) -> None:
        payload = {"data": {"resultJson": {"urls": ["https://cdn.kie.ai/img/c.png"]}}}
        assert KieClient.extract_result_urls(payload) == ["https://cdn.kie.ai/img/c.png"]

    def test_filters_non_http_urls(self) -> None:
        payload = {"data": {"resultJson": json.dumps({"resultUrls": ["ftp://bad.com/x.png", "https://good.com/x.png"]})}}
        assert KieClient.extract_result_urls(payload) == ["https://good.com/x.png"]

    def test_http_urls_accepted(self) -> None:
        payload = {"data": {"resultJson": {"resultUrls": ["http://cdn.example.com/x.png"]}}}
        assert KieClient.extract_result_urls(payload) == ["http://cdn.example.com/x.png"]

    def test_invalid_json_string_returns_empty(self) -> None:
        payload = {"data": {"resultJson": "not-json"}}
        assert KieClient.extract_result_urls(payload) == []

    def test_multiple_urls_returned(self) -> None:
        urls = ["https://cdn.kie.ai/img/1.png", "https://cdn.kie.ai/img/2.png"]
        payload = {"data": {"resultJson": {"resultUrls": urls}}}
        assert KieClient.extract_result_urls(payload) == urls
