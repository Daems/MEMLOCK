from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import requests


VALID_ASPECTS = {"1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "auto"}
VALID_RESOLUTIONS = {"1K", "2K", "4K"}
VALID_FORMATS = {"png", "jpg"}


@dataclass
class KieClient:
    api_key: str
    base_url: str = "https://api.kie.ai"
    timeout: int = 60

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def build_task_payload(
        self,
        *,
        prompt: str,
        image_input: list[str] | None = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        output_format: str = "png",
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        if not prompt.strip():
            raise ValueError("prompt cannot be empty")
        if aspect_ratio not in VALID_ASPECTS:
            raise ValueError(f"Unsupported aspect_ratio {aspect_ratio!r}; use one of {sorted(VALID_ASPECTS)}")
        if resolution not in VALID_RESOLUTIONS:
            raise ValueError(f"Unsupported resolution {resolution!r}; use one of {sorted(VALID_RESOLUTIONS)}")
        if output_format not in VALID_FORMATS:
            raise ValueError(f"Unsupported output_format {output_format!r}; use one of {sorted(VALID_FORMATS)}")

        payload: dict[str, Any] = {
            "model": "nano-banana-pro",
            "input": {
                "prompt": prompt,
                "image_input": image_input or [],
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "output_format": output_format,
            },
        }
        if callback_url:
            payload["callBackUrl"] = callback_url
        return payload

    def create_nano_banana_pro_task(
        self,
        *,
        prompt: str,
        image_input: list[str] | None = None,
        aspect_ratio: str = "1:1",
        resolution: str = "1K",
        output_format: str = "png",
        callback_url: str | None = None,
    ) -> dict[str, Any]:
        payload = self.build_task_payload(
            prompt=prompt,
            image_input=image_input,
            aspect_ratio=aspect_ratio,
            resolution=resolution,
            output_format=output_format,
            callback_url=callback_url,
        )
        url = f"{self.base_url}/api/v1/jobs/createTask"
        response = requests.post(url, headers=self.headers, json=payload, timeout=self.timeout)
        return self._decode_response(response)

    def get_task(self, task_id: str) -> dict[str, Any]:
        if not task_id:
            raise ValueError("task_id cannot be empty")
        url = f"{self.base_url}/api/v1/jobs/recordInfo"
        response = requests.get(url, headers={"Authorization": f"Bearer {self.api_key}"}, params={"taskId": task_id}, timeout=self.timeout)
        return self._decode_response(response)

    def wait_for_task(
        self,
        task_id: str,
        *,
        timeout_seconds: int = 900,
        initial_delay: float = 2.0,
        max_delay: float = 20.0,
    ) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        delay = initial_delay

        while True:
            result = self.get_task(task_id)
            data = result.get("data") or {}
            state = str(data.get("state", "")).lower()

            if state in {"success", "fail"}:
                return result
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Timed out waiting for task {task_id}; latest state={state!r}")

            time.sleep(delay)
            delay = min(max_delay, delay * 1.5)

    @staticmethod
    def extract_result_urls(task_response: dict[str, Any]) -> list[str]:
        data = task_response.get("data") or {}
        result_json = data.get("resultJson") or data.get("result_json") or ""
        if isinstance(result_json, dict):
            parsed = result_json
        else:
            try:
                parsed = json.loads(result_json) if result_json else {}
            except json.JSONDecodeError:
                return []

        urls = parsed.get("resultUrls") or parsed.get("result_urls") or parsed.get("urls") or []
        return [str(u) for u in urls if isinstance(u, str) and u.startswith(("http://", "https://"))]

    @staticmethod
    def _decode_response(response: requests.Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            response.raise_for_status()
            raise RuntimeError("API returned non-JSON response")

        if not response.ok:
            raise RuntimeError(f"Kie API HTTP {response.status_code}: {body}")
        if isinstance(body, dict) and body.get("code") not in (None, 200, 505):
            # Kie docs show some successful query examples using code 505 with msg=success.
            msg = body.get("msg", "unknown API error")
            if str(msg).lower() != "success":
                raise RuntimeError(f"Kie API error: {body}")
        return body
