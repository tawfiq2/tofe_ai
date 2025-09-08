"""Download OutSystems application or module source code via the LifeTime API.

The script implements the API flow documented by OutSystems for fetching the
source code of running applications or modules. It supports both names and keys
for the target environment and application/module.

Example usage:

    python outsystems_source_download.py \
        --env Testing --app EmployeeBackoffice --output app.zip

    python outsystems_source_download.py \
        --env Testing --module EmployeeBackoffice --output module.zip

Authentication and host configuration are provided through environment
variables:

* ``LIFETIME_BASE`` – the base URL of the LifeTime server, e.g.
  ``https://hostname.outsystems.com``
* ``LIFETIME_TOKEN`` – API token with the necessary privileges
"""

from __future__ import annotations

import argparse
import os
import time
import uuid
from typing import Optional

import requests


def _headers() -> dict[str, str]:
    token = os.getenv("LIFETIME_TOKEN")
    if not token:
        raise SystemExit("LIFETIME_TOKEN environment variable not set")
    return {"Authorization": f"Bearer {token}"}


def _base_url() -> str:
    base = os.getenv("LIFETIME_BASE")
    if not base:
        raise SystemExit("LIFETIME_BASE environment variable not set")
    return base.rstrip("/")


def _resolve_key(name_or_key: str, endpoint: str) -> str:
    """Return the GUID for a given entity name or key."""
    try:
        uuid.UUID(name_or_key)
        return name_or_key
    except ValueError:
        url = f"{_base_url()}/lifetimeapi/rest/v2/{endpoint}/"
        resp = requests.get(url, headers=_headers(), timeout=30)
        resp.raise_for_status()
        for item in resp.json():
            if item.get("Name", "").lower() == name_or_key.lower():
                return item["Key"]
        raise SystemExit(f"{endpoint[:-1].capitalize()} '{name_or_key}' not found")


def _wait_for_package(status_url: str) -> None:
    while True:
        resp = requests.get(status_url, headers=_headers(), timeout=30)
        resp.raise_for_status()
        status = resp.json().get("Status")
        if status == "Done":
            return
        if status == "Error":
            raise SystemExit("Packaging failed")
        time.sleep(2)


def _download(download_url: str, output: str) -> None:
    resp = requests.get(download_url, headers=_headers(), timeout=60)
    resp.raise_for_status()
    with open(output, "wb") as handle:
        handle.write(resp.content)


def download_application(env: str, app: str, output: str) -> None:
    env_key = _resolve_key(env, "environments")
    app_key = _resolve_key(app, "applications")
    base = _base_url()

    resp = requests.post(
        f"{base}/lifetimeapi/rest/v2/environments/{env_key}/applications/{app_key}/sourcecodeaccess",
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    package_key = resp.json()["PackageKey"]

    status_url = (
        f"{base}/lifetimeapi/rest/v2/environments/{env_key}/applications/{app_key}"
        f"/sourcecodeaccess/{package_key}/status"
    )
    _wait_for_package(status_url)

    resp = requests.get(
        f"{base}/lifetimeapi/rest/v2/environments/{env_key}/applications/{app_key}"
        f"/sourcecodeaccess/{package_key}/download",
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    download_url: str = resp.json()["url"]
    _download(download_url, output)


def download_module(env: str, module: str, output: str) -> None:
    env_key = _resolve_key(env, "environments")
    mod_key = _resolve_key(module, "modules")
    base = _base_url()

    resp = requests.post(
        f"{base}/lifetimeapi/rest/v2/environments/{env_key}/modules/{mod_key}/sourcecodeaccess",
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    package_key = resp.json()["PackageKey"]

    status_url = (
        f"{base}/lifetimeapi/rest/v2/environments/{env_key}/modules/{mod_key}"
        f"/sourcecodeaccess/{package_key}/status"
    )
    _wait_for_package(status_url)

    resp = requests.get(
        f"{base}/lifetimeapi/rest/v2/environments/{env_key}/modules/{mod_key}"
        f"/sourcecodeaccess/{package_key}/download",
        headers=_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    download_url: str = resp.json()["url"]
    _download(download_url, output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download OutSystems source code")
    parser.add_argument("--env", required=True, help="Environment name or key")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--app", help="Application name or key")
    group.add_argument("--module", help="Module name or key")
    parser.add_argument("--output", required=True, help="Path to save the package")
    args = parser.parse_args()

    if args.app:
        download_application(args.env, args.app, args.output)
    else:
        download_module(args.env, args.module, args.output)


if __name__ == "__main__":
    main()
