from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

import yaml

from .config import load_settings
from .kie_client import KieClient
from .storage import download_urls, upsert_task


def build_client() -> tuple[KieClient, Any]:
    settings = load_settings()
    return KieClient(api_key=settings.api_key, base_url=settings.base_url), settings


def cmd_submit(args: argparse.Namespace) -> None:
    client, settings = build_client()
    response = client.create_nano_banana_pro_task(
        prompt=args.prompt,
        image_input=args.image_input or [],
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        output_format=args.output_format,
        callback_url=args.callback_url if args.callback_url is not None else settings.callback_url,
    )
    task_id = response.get("data", {}).get("taskId")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    if task_id:
        upsert_task(settings.db_path, task_id, prompt=args.prompt, response=response)
    if args.download and task_id:
        poll_and_download(client, settings, task_id, args.prompt)


def cmd_submit_yaml(args: argparse.Namespace) -> None:
    client, settings = build_client()
    job = yaml.safe_load(Path(args.path).read_text(encoding="utf-8"))
    prompt = job["prompt"]
    response = client.create_nano_banana_pro_task(
        prompt=prompt,
        image_input=job.get("image_input") or [],
        aspect_ratio=job.get("aspect_ratio", settings.default_aspect_ratio),
        resolution=job.get("resolution", settings.default_resolution),
        output_format=job.get("output_format", settings.default_output_format),
        callback_url=job.get("callback_url") or settings.callback_url,
    )
    task_id = response.get("data", {}).get("taskId")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    if task_id:
        upsert_task(settings.db_path, task_id, prompt=prompt, response=response)
    if args.download and task_id:
        poll_and_download(client, settings, task_id, prompt)


def cmd_poll(args: argparse.Namespace) -> None:
    client, settings = build_client()
    response = client.wait_for_task(args.task_id, timeout_seconds=args.timeout)
    print(json.dumps(response, indent=2, ensure_ascii=False))
    data = response.get("data", {})
    upsert_task(settings.db_path, args.task_id, state=data.get("state", "unknown"), response=response)
    if args.download:
        urls = client.extract_result_urls(response)
        paths = download_urls(urls, settings.output_dir, prefix=args.task_id)
        for path in paths:
            print(f"downloaded: {path}")


def poll_and_download(client: KieClient, settings: Any, task_id: str, prompt: str) -> None:
    response = client.wait_for_task(task_id)
    data = response.get("data", {})
    upsert_task(settings.db_path, task_id, state=data.get("state", "unknown"), prompt=prompt, response=response)
    urls = client.extract_result_urls(response)
    paths = download_urls(urls, settings.output_dir, prefix=task_id)
    for path in paths:
        print(f"downloaded: {path}")


def cmd_batch(args: argparse.Namespace) -> None:
    client, settings = build_client()
    csv_path = Path(args.path)
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prompt = row.get("prompt", "").strip()
            if not prompt:
                continue
            image_input = [u.strip() for u in (row.get("image_input") or "").split("|") if u.strip()]
            response = client.create_nano_banana_pro_task(
                prompt=prompt,
                image_input=image_input,
                aspect_ratio=row.get("aspect_ratio") or settings.default_aspect_ratio,
                resolution=row.get("resolution") or settings.default_resolution,
                output_format=row.get("output_format") or settings.default_output_format,
                callback_url=row.get("callback_url") or settings.callback_url,
            )
            task_id = response.get("data", {}).get("taskId")
            print(json.dumps({"prompt": prompt[:80], "response": response}, ensure_ascii=False))
            if task_id:
                upsert_task(settings.db_path, task_id, prompt=prompt, response=response)
                if args.download:
                    poll_and_download(client, settings, task_id, prompt)


def main() -> None:
    parser = argparse.ArgumentParser(description="Nano Banana Pro automation CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    submit = sub.add_parser("submit", help="Submit a single prompt")
    submit.add_argument("--prompt", required=True)
    submit.add_argument("--image-input", action="append", help="Public URL to a reference/input image. Repeat as needed.")
    submit.add_argument("--aspect-ratio", default="1:1")
    submit.add_argument("--resolution", default="1K")
    submit.add_argument("--output-format", default="png", choices=["png", "jpg"])
    submit.add_argument("--callback-url", default=None)
    submit.add_argument("--download", action="store_true")
    submit.set_defaults(func=cmd_submit)

    submit_yaml = sub.add_parser("submit-yaml", help="Submit a YAML job file")
    submit_yaml.add_argument("path")
    submit_yaml.add_argument("--download", action="store_true")
    submit_yaml.set_defaults(func=cmd_submit_yaml)

    poll = sub.add_parser("poll", help="Poll a task until completion")
    poll.add_argument("task_id")
    poll.add_argument("--timeout", type=int, default=900)
    poll.add_argument("--download", action="store_true")
    poll.set_defaults(func=cmd_poll)

    batch = sub.add_parser("batch", help="Submit a CSV batch")
    batch.add_argument("path")
    batch.add_argument("--download", action="store_true")
    batch.set_defaults(func=cmd_batch)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
