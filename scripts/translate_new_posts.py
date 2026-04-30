#!/usr/bin/env python3
"""Auto-translate newly added Hugo posts to Traditional Chinese."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
import urllib.request

import yaml

DEFAULT_CONTENT_ROOT = "content/posts"
DEFAULT_TARGET_LANG = "zh-tw"
DEFAULT_MODEL = "gpt-4.1-mini"
DEFAULT_API_URL = "https://api.openai.com/v1/chat/completions"
TRANSLATABLE_FRONTMATTER_FIELDS = ("title", "summary", "description")

SYSTEM_PROMPT = textwrap.dedent(
    """
    You are a professional translator.
    Translate the user's Markdown content from English to Traditional Chinese (Taiwan).
    Preserve Markdown formatting, headings, lists, blockquotes, tables, and line breaks.
    Do NOT translate code blocks, inline code, URLs, image paths, filenames, config values, or frontmatter keys.
    Keep link targets, image paths, and code snippets exactly as-is.
    Use natural Traditional Chinese wording suitable for Taiwan.
    Return only the translated Markdown content.
    """
).strip()


def run_git_diff(base_sha: str, head_sha: str) -> list[str]:
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-status",
            "--diff-filter=A",
            base_sha,
            head_sha,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    added_files: list[str] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", 1)
        if len(parts) != 2:
            continue
        status, path = parts
        if status != "A":
            continue
        added_files.append(path)
    return added_files


def split_frontmatter(raw: str) -> tuple[dict, str]:
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, raw
    end_index = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, raw
    frontmatter_text = "\n".join(lines[1:end_index]) + "\n"
    body = "\n".join(lines[end_index + 1 :])
    if raw.endswith("\n"):
        body += "\n"
    frontmatter = yaml.safe_load(frontmatter_text) or {}
    if not isinstance(frontmatter, dict):
        raise ValueError("Frontmatter must be a mapping.")
    return frontmatter, body


def serialize_frontmatter(frontmatter: dict) -> str:
    return yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).rstrip() + "\n"


def build_translation_key(source_path: Path) -> str:
    stem = source_path.stem
    return stem


def target_path_for(source_path: Path, lang_suffix: str) -> Path:
    # Hugo multilingual best practice: keep translations beside the source file
    # using the .<lang>.md suffix so Hugo can link translations automatically.
    return source_path.with_name(f"{source_path.stem}.{lang_suffix}{source_path.suffix}")


def should_skip(frontmatter: dict, include_drafts: bool) -> tuple[bool, str | None]:
    if frontmatter.get("translation") is False:
        return True, "translation disabled"
    if frontmatter.get("draft") is True and not include_drafts:
        return True, "draft post"
    lang = str(frontmatter.get("lang", "en")).lower()
    if lang not in {"en", "en-us", "en-gb"}:
        return True, f"source lang is {lang}"
    return False, None


def call_translation_api(api_url: str, api_key: str, model: str, content: str) -> str:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        "temperature": 0.2,
    }

    # Swap the model or API endpoint here if you prefer a different provider.
    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise RuntimeError(f"Translation API error ({exc.code}): {detail}") from exc

    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Unexpected translation response: {data}") from exc


def translate_text(text: str, api_url: str, api_key: str, model: str) -> str:
    if not text.strip():
        return text
    return call_translation_api(api_url, api_key, model, text)


def translate_file(
    source_path: Path,
    target_lang: str,
    add_metadata: bool,
    include_drafts: bool,
    api_url: str,
    api_key: str,
    model: str,
) -> Path | None:
    raw = source_path.read_text(encoding="utf-8")
    frontmatter, body = split_frontmatter(raw)

    skip, reason = should_skip(frontmatter, include_drafts)
    if skip:
        print(f"Skipping {source_path}: {reason}")
        return None

    target_path = target_path_for(source_path, target_lang)
    if target_path.exists():
        print(f"Skipping {source_path}: translation already exists")
        return None

    translated_frontmatter = dict(frontmatter)

    for key in TRANSLATABLE_FRONTMATTER_FIELDS:
        value = translated_frontmatter.get(key)
        if isinstance(value, str):
            translated_frontmatter[key] = translate_text(value, api_url, api_key, model)

    translation_key = translated_frontmatter.get("translationKey") or build_translation_key(source_path)
    translated_frontmatter["translationKey"] = translation_key
    translated_frontmatter["lang"] = target_lang

    if add_metadata:
        translated_frontmatter["translationGenerated"] = True
        translated_frontmatter["translatedFrom"] = str(source_path)

    translated_body = translate_text(body, api_url, api_key, model)

    serialized = "---\n" + serialize_frontmatter(translated_frontmatter) + "---\n\n" + translated_body
    target_path.write_text(serialized, encoding="utf-8")
    print(f"Created {target_path}")
    return target_path


def resolve_commit_range(base_sha: str | None, head_sha: str | None) -> tuple[str, str]:
    if base_sha and set(base_sha) == {"0"}:
        base_sha = None
    if base_sha and head_sha:
        return base_sha, head_sha

    resolved_head = head_sha or subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
    resolved_base = base_sha
    if not resolved_base:
        resolved_base = subprocess.check_output(["git", "rev-parse", "HEAD~1"]).decode().strip()
    return resolved_base, resolved_head


def main() -> int:
    parser = argparse.ArgumentParser(description="Translate newly added Hugo posts to Traditional Chinese.")
    parser.add_argument("--base", dest="base_sha", default=os.getenv("BASE_SHA"))
    parser.add_argument("--head", dest="head_sha", default=os.getenv("HEAD_SHA"))
    parser.add_argument("--content-root", default=os.getenv("CONTENT_ROOT", DEFAULT_CONTENT_ROOT))
    parser.add_argument("--target-lang", default=os.getenv("TARGET_LANG", DEFAULT_TARGET_LANG))
    parser.add_argument("--api-url", default=os.getenv("TRANSLATION_API_URL", DEFAULT_API_URL))
    parser.add_argument("--model", default=os.getenv("TRANSLATION_MODEL", DEFAULT_MODEL))
    args = parser.parse_args()

    include_drafts = os.getenv("INCLUDE_DRAFTS", "false").lower() in {"1", "true", "yes"}
    add_metadata = os.getenv("ADD_TRANSLATION_METADATA", "true").lower() in {"1", "true", "yes"}

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY is not set.", file=sys.stderr)
        return 1

    base_sha, head_sha = resolve_commit_range(args.base_sha, args.head_sha)
    try:
        added_files = run_git_diff(base_sha, head_sha)
    except subprocess.CalledProcessError as exc:
        print(exc.stderr, file=sys.stderr)
        return exc.returncode

    content_root = Path(args.content_root)
    translated_any = False

    for path_str in added_files:
        path = Path(path_str)
        if not path.is_file():
            continue
        if path.suffix.lower() != ".md":
            continue
        if path.name.endswith(f".{args.target_lang}{path.suffix}"):
            continue
        try:
            path.relative_to(content_root)
        except ValueError:
            continue

        created = translate_file(
            path,
            args.target_lang,
            add_metadata,
            include_drafts,
            args.api_url,
            api_key,
            args.model,
        )
        if created:
            translated_any = True

    if not translated_any:
        print("No translations generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
