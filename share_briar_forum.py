#!/usr/bin/env python3
"""CLI utility to create shareable Briar forum payloads.

The script builds a compact JSON payload and encodes it as URL-safe Base64.
This does not depend on undocumented Briar internals; it creates a portable
payload that can be sent through messengers, e-mail, or QR generators.
"""

from __future__ import annotations

import argparse
import base64
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SCHEME = "briar-forum://share/"


def _urlsafe_b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("utf-8").rstrip("=")


def build_payload(
    forum_id: str,
    forum_name: str,
    owner: str,
    description: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "forum_id": forum_id,
        "forum_name": forum_name,
        "owner": owner,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "version": 1,
    }

    if description:
        payload["description"] = description
    if tags:
        payload["tags"] = tags

    return payload


def build_share_link(payload: dict[str, Any], scheme: str = DEFAULT_SCHEME) -> str:
    raw = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return f"{scheme}{_urlsafe_b64encode(raw)}"


def save_output(link: str, payload: dict[str, Any], output: Path) -> None:
    artifact = {
        "share_link": link,
        "payload": payload,
    }
    output.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a shareable Briar forum invitation payload."
    )
    parser.add_argument("forum_id", help="Stable forum identifier, e.g. tech-room-42")
    parser.add_argument("forum_name", help="Public forum name shown to recipients")
    parser.add_argument("owner", help="Forum owner or moderator name/contact")
    parser.add_argument(
        "--description",
        default=None,
        help="Optional description shown in preview",
    )
    parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        default=None,
        help="Forum tag (repeatable)",
    )
    parser.add_argument(
        "--scheme",
        default=DEFAULT_SCHEME,
        help=f"URL scheme prefix (default: {DEFAULT_SCHEME})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to JSON file with payload and link",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    payload = build_payload(
        forum_id=args.forum_id,
        forum_name=args.forum_name,
        owner=args.owner,
        description=args.description,
        tags=args.tags,
    )
    share_link = build_share_link(payload, scheme=args.scheme)

    print("Share link:")
    print(share_link)
    print("\nMarkdown snippet:")
    print(f"[Join forum: {payload['forum_name']}]({share_link})")

    if args.output:
        save_output(share_link, payload, args.output)
        print(f"\nSaved JSON artifact to: {args.output}")


if __name__ == "__main__":
    main()
