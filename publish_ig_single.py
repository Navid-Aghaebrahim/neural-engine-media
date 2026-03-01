#!/usr/bin/env python3
"""Publish a single-image IG post via Instagram Graph API.

Usage:
  python3 publish_ig_single.py <image_url_or_repo_path> <caption>

Notes:
- Instagram Graph requires a PUBLICLY-REACHABLE URL.
- If you pass a repo-relative path like: assets/ig/2026-02-28-PM-foo.png
  this script will convert it to a raw GitHub URL on the main branch.
"""

import os
import sys
import time
from typing import Final

import requests

TOKEN: Final[str] = os.environ["META_ACCESS_TOKEN"]
IG_ID: Final[str] = os.environ["INSTAGRAM_IG_BUSINESS_ID"]
BASE: Final[str] = "https://graph.facebook.com/v22.0"
RAW_BASE: Final[str] = "https://raw.githubusercontent.com/Navid-Aghaebrahim/neural-engine-media/main"


def api(method, path, **kwargs):
    url = f"{BASE}/{path}"
    kwargs.setdefault("params", {})["access_token"] = TOKEN
    r = getattr(requests, method)(url, **kwargs)
    data = r.json()
    if "error" in data:
        print(f"API ERROR: {data['error']}", file=sys.stderr)
        sys.exit(1)
    return data


def to_public_url(image_url_or_path: str) -> str:
    if image_url_or_path.startswith("http://") or image_url_or_path.startswith("https://"):
        return image_url_or_path
    p = image_url_or_path.lstrip("/")
    return f"{RAW_BASE}/{p}"


image_url = to_public_url(sys.argv[1])
caption = sys.argv[2]

# Step 1 — create container
print("Creating media container...")
container = api("post", f"{IG_ID}/media",
                data={"image_url": image_url, "caption": caption})
container_id = container["id"]
print(f"Container id: {container_id}")

# Step 2 — wait for container to be ready
for attempt in range(12):
    status = api("get", container_id, params={"fields": "status_code"})
    sc = status.get("status_code", "UNKNOWN")
    print(f"  status_code: {sc}")
    if sc == "FINISHED":
        break
    if sc == "ERROR":
        print("Container error — aborting.", file=sys.stderr)
        sys.exit(1)
    time.sleep(5)
else:
    print("Container never became FINISHED.", file=sys.stderr)
    sys.exit(1)

# Step 3 — publish
print("Publishing...")
pub = api("post", f"{IG_ID}/media_publish",
          data={"creation_id": container_id})
media_id = pub["id"]
print(f"Published! media_id={media_id}")

# Step 4 — get permalink
info = api("get", media_id, params={"fields": "permalink"})
print(f"Permalink: {info.get('permalink','(n/a)')}")
print(f"MEDIA_ID:{media_id}")
print(f"PERMALINK:{info.get('permalink','')}")
