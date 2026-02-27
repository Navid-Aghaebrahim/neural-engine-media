#!/usr/bin/env python3
"""fal.ai helper for Neural-Engine media generation.

Uses synchronous Model Endpoint API via https://fal.run/<model>.
Auth: reads FAL_KEY (preferred) or FAL_API_KEY.

Returns downloaded image as PIL.Image.
"""

from __future__ import annotations

import os
import time
from io import BytesIO
from typing import Any, Dict, Optional

import requests
from PIL import Image


class FalError(RuntimeError):
    pass


def _get_fal_key() -> str:
    key = os.environ.get("FAL_KEY") or os.environ.get("FAL_API_KEY")
    if not key:
        raise FalError("Missing fal.ai credentials. Set env FAL_KEY (preferred) or FAL_API_KEY")
    return key


def generate_image(
    *,
    prompt: str,
    model: str = "fal-ai/flux/dev",
    image_size: str = "square_hd",
    seed: Optional[int] = None,
    extra: Optional[Dict[str, Any]] = None,
    timeout_s: int = 120,
) -> Image.Image:
    """Generate one image with fal.ai and return it as a PIL Image."""

    key = _get_fal_key()
    url = f"https://fal.run/{model}"

    payload: Dict[str, Any] = {
        "prompt": prompt,
        "image_size": image_size,
    }
    if seed is not None:
        payload["seed"] = seed
    if extra:
        payload.update(extra)

    resp = requests.post(
        url,
        headers={"Authorization": f"Key {key}"},
        json=payload,
        timeout=timeout_s,
    )
    if resp.status_code >= 400:
        raise FalError(f"fal.run error {resp.status_code}: {resp.text[:500]}")

    data = resp.json()
    images = data.get("images") or []
    if not images:
        raise FalError(f"fal.run returned no images. keys={list(data.keys())}")

    img_url = images[0].get("url")
    if not img_url:
        raise FalError(f"fal.run response missing images[0].url")

    # Download
    dl = requests.get(img_url, timeout=timeout_s)
    if dl.status_code >= 400:
        raise FalError(f"image download error {dl.status_code}: {img_url}")

    # give CDN a beat if needed
    if not dl.content:
        time.sleep(0.5)
        dl = requests.get(img_url, timeout=timeout_s)

    return Image.open(BytesIO(dl.content)).convert("RGBA")
