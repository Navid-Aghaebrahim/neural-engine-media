#!/usr/bin/env python3
"""Publish an Instagram CAROUSEL post (multi-image) via Instagram Graph API.

Usage:
  python3 publish_ig_carousel.py <caption> <image_url1> <image_url2> [image_url3 ...]

Env:
  META_ACCESS_TOKEN
  INSTAGRAM_IG_BUSINESS_ID

Notes:
- Creates one media container per image with is_carousel_item=true
- Creates a parent container with media_type=CAROUSEL and children=<ids>
- Publishes the parent container
"""

import os
import sys
import time
import requests

TOKEN = os.environ["META_ACCESS_TOKEN"]
IG_ID = os.environ["INSTAGRAM_IG_BUSINESS_ID"]
BASE = "https://graph.facebook.com/v22.0"


def api(method: str, path: str, **kwargs):
    url = f"{BASE}/{path}"
    params = kwargs.setdefault("params", {})
    params["access_token"] = TOKEN
    r = getattr(requests, method)(url, **kwargs)
    data = r.json()
    if "error" in data:
        print(f"API ERROR: {data['error']}", file=sys.stderr)
        sys.exit(1)
    return data


def wait_container(container_id: str, label: str, max_attempts: int = 24, sleep_s: int = 5):
    for attempt in range(max_attempts):
        status = api("get", container_id, params={"fields": "status_code"})
        sc = status.get("status_code", "UNKNOWN")
        print(f"  {label} status_code: {sc}")
        if sc == "FINISHED":
            return
        if sc == "ERROR":
            print(f"{label} container error — aborting.", file=sys.stderr)
            sys.exit(1)
        time.sleep(sleep_s)
    print(f"{label} container never became FINISHED.", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) < 4:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)

    caption = sys.argv[1]
    image_urls = sys.argv[2:]

    if not (3 <= len(image_urls) <= 10):
        print("Carousel must have 3–10 images.", file=sys.stderr)
        sys.exit(2)

    # Step 1 — create child containers
    children = []
    for i, url in enumerate(image_urls, start=1):
        print(f"Creating child container {i}/{len(image_urls)}...")
        child = api(
            "post",
            f"{IG_ID}/media",
            data={
                "image_url": url,
                "is_carousel_item": "true",
            },
        )
        cid = child["id"]
        print(f"  child container id: {cid}")
        wait_container(cid, label=f"child[{i}]")
        children.append(cid)

    # Step 2 — create parent carousel container
    print("Creating parent carousel container...")
    parent = api(
        "post",
        f"{IG_ID}/media",
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(children),
            "caption": caption,
        },
    )
    parent_id = parent["id"]
    print(f"Parent container id: {parent_id}")
    wait_container(parent_id, label="parent")

    # Step 3 — publish
    print("Publishing...")
    pub = api("post", f"{IG_ID}/media_publish", data={"creation_id": parent_id})
    media_id = pub["id"]
    print(f"Published! media_id={media_id}")

    # Step 4 — permalink
    info = api("get", media_id, params={"fields": "permalink"})
    print(f"Permalink: {info.get('permalink','(n/a)')}")
    print(f"MEDIA_ID:{media_id}")
    print(f"PERMALINK:{info.get('permalink','')}")


if __name__ == "__main__":
    main()
