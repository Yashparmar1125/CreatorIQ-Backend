from __future__ import annotations

import os
import re
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.core.config import settings


def _resolve_api_key() -> str:
    raw_key = settings.YOUTUBE_API_KEY or os.getenv("GOOGLE_API_KEY") or ""
    key = raw_key.strip().strip('"').strip("'")
    if not key:
        raise ValueError("YOUTUBE_API_KEY is not configured")
    return key


def _raise_readable_youtube_error(exc: HttpError) -> None:
    status = getattr(exc.resp, "status", None)
    content = ""
    try:
        content = exc.content.decode("utf-8") if exc.content else ""
    except Exception:
        content = str(exc)

    lower_content = content.lower()
    if status == 400 and "api key not found" in lower_content:
        raise ValueError(
            "YouTube API rejected the key as invalid. Regenerate a Server API key, enable YouTube Data API v3, and update YOUTUBE_API_KEY."
        ) from exc
    if status == 403 and "referer" in lower_content:
        raise ValueError(
            "API key is restricted to browser referrers. Use a Server key with IP/no referrer restriction for backend calls."
        ) from exc
    if status == 403 and "ip" in lower_content:
        raise ValueError(
            "API key IP restriction does not include this machine/server IP."
        ) from exc
    if status == 403 and "accessnotconfigured" in lower_content:
        raise ValueError("Enable YouTube Data API v3 for this Google Cloud project.") from exc
    if status == 403 and "quota" in lower_content:
        raise ValueError("YouTube API quota exceeded for this key/project.") from exc

    raise ValueError(f"YouTube API error ({status}): {content[:240]}") from exc


def _normalize_username(username: str) -> str:
    normalized = username.strip()
    if normalized.startswith("@"):
        normalized = normalized[1:]
    return normalized


def _label_from_topic_url(topic_url: str) -> str:
    # Topic URLs usually end with a slug-like token; convert that into readable text.
    tail = topic_url.rstrip("/").split("/")[-1]
    tail = re.sub(r"[_-]+", " ", tail)
    tail = re.sub(r"\s+", " ", tail).strip()

    if not tail:
        return "General"

    keyword_map = {
        "music": "Music",
        "gaming": "Gaming",
        "sport": "Sports",
        "movie": "Entertainment",
        "film": "Entertainment",
        "tech": "Technology",
        "science": "Science",
        "news": "News",
        "food": "Food",
        "fashion": "Fashion",
        "beauty": "Beauty",
        "education": "Education",
        "finance": "Finance",
        "business": "Business",
        "travel": "Travel",
    }

    lower_tail = tail.lower()
    for key, label in keyword_map.items():
        if key in lower_tail:
            return label

    return tail.title()


def _resolve_channel_id(youtube: Any, username: str) -> str:
    if username.startswith("UC") and len(username) >= 20:
        return username

    channel_lookup = (
        youtube.channels()
        .list(part="id", forUsername=username, maxResults=1)
        .execute()
    )
    channel_items = channel_lookup.get("items", [])
    if channel_items:
        return channel_items[0]["id"]

    search_lookup = (
        youtube.search()
        .list(part="snippet", q=username, type="channel", maxResults=1)
        .execute()
    )
    search_items = search_lookup.get("items", [])
    if search_items:
        return search_items[0]["snippet"]["channelId"]

    raise ValueError(f"No YouTube channel found for '{username}'")


def resolve_youtube_channel_genre(username: str) -> dict[str, Any]:
    api_key = _resolve_api_key()

    cleaned_username = _normalize_username(username)
    if not cleaned_username:
        raise ValueError("Username cannot be empty")

    youtube = build("youtube", "v3", developerKey=api_key, cache_discovery=False)

    try:
        channel_id = _resolve_channel_id(youtube, cleaned_username)
    except HttpError as exc:
        _raise_readable_youtube_error(exc)

    try:
        channel_response = (
            youtube.channels()
            .list(part="snippet,topicDetails", id=channel_id, maxResults=1)
            .execute()
        )
    except HttpError as exc:
        _raise_readable_youtube_error(exc)
    items = channel_response.get("items", [])
    if not items:
        raise ValueError(f"Channel metadata not found for '{cleaned_username}'")

    channel = items[0]
    channel_title = channel.get("snippet", {}).get("title", cleaned_username)
    topic_urls = channel.get("topicDetails", {}).get("topicCategories", [])
    genre_signals = [_label_from_topic_url(topic_url) for topic_url in topic_urls]

    if genre_signals:
        genre = genre_signals[0]
    else:
        # Fallback when topicDetails are unavailable for smaller/new channels.
        genre = "Creator Economy"
        genre_signals = [genre]

    return {
        "username": cleaned_username,
        "channel_id": channel_id,
        "channel_title": channel_title,
        "genre": genre,
        "genre_signals": genre_signals,
    }
