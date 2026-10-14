#!/usr/bin/env python3
"""Refresh the generated lists in README.md.

Fills the blocks between the <!-- name:start --> / <!-- name:end --> markers
with data from the GitHub API. Standard library only. Uses GITHUB_TOKEN if set
(higher rate limit), works without it.

    python scripts/update_readme.py            # rewrite README.md
    python scripts/update_readme.py --dry-run  # print the result instead
"""

import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

USER = "dxmoc"
API = "https://api.github.com"
README = Path(__file__).resolve().parent.parent / "README.md"
MAX_RELEASES = 5
MAX_ELSEWHERE = 5


def get(path: str, params: dict | None = None):
    url = f"{API}{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": f"{USER}-profile-readme",
    })
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def day(timestamp: str) -> str:
    return timestamp[:10]


def recent_releases() -> list[str]:
    # /users/<name>/repos only ever lists public repositories.
    repos = get(f"/users/{USER}/repos", {"type": "owner", "per_page": 100})
    found = []
    for repo in repos:
        if repo["fork"] or repo["archived"]:
            continue
        releases = get(f"/repos/{repo['full_name']}/releases", {"per_page": 1})
        if not releases:
            continue
        rel = releases[0]
        if rel["draft"]:
            continue
        found.append((rel["published_at"], repo["name"], rel["tag_name"], rel["html_url"]))
    found.sort(reverse=True)
    return [
        f"[{name} {tag}]({url}) <sub>{day(when)}</sub>"
        for when, name, tag, url in found[:MAX_RELEASES]
    ]


def elsewhere() -> list[str]:
    # Issues and pull requests in other people's repositories that I opened,
    # commented on or was mentioned in.
    query = f"involves:{USER} -user:{USER} is:public"
    result = get("/search/issues", {"q": query, "sort": "updated", "order": "desc", "per_page": MAX_ELSEWHERE})
    lines = []
    for item in result.get("items", []):
        repo = item["repository_url"].removeprefix(f"{API}/repos/")
        kind = "PR" if "pull_request" in item else "issue"
        title = item["title"].replace("[", "(").replace("]", ")").replace("|", "/")
        lines.append(
            f"[{repo}#{item['number']}]({item['html_url']}) {kind}: {title} <sub>{day(item['updated_at'])}</sub>"
        )
    return lines


def fill(text: str, name: str, lines: list[str]) -> str:
    body = "\n\n".join(lines) if lines else "_Nothing yet._"
    pattern = re.compile(rf"(<!-- {name}:start -->).*?(<!-- {name}:end -->)", re.S)
    if not pattern.search(text):
        raise SystemExit(f"marker '{name}' not found in {README}")
    return pattern.sub(lambda m: f"{m.group(1)}\n{body}\n{m.group(2)}", text)


def main() -> None:
    text = README.read_text(encoding="utf-8")
    new = fill(text, "releases", recent_releases())
    new = fill(new, "elsewhere", elsewhere())
    if "--dry-run" in sys.argv:
        print(new)
        return
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README.md updated")
    else:
        print("README.md unchanged")


if __name__ == "__main__":
    main()
