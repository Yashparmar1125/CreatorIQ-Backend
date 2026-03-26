from __future__ import annotations

from typing import List

from pytrends.request import TrendReq


def get_top_trending_topics(keyword: str, top_n: int = 5) -> List[str]:
    """Fetch top rising YouTube-related topics for the given keyword."""
    cleaned_keyword = keyword.strip()
    if not cleaned_keyword:
        return []

    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(
        [cleaned_keyword],
        cat=0,
        timeframe="now 7-d",
        geo="",
        gprop="youtube",
    )

    related_queries = pytrends.related_queries()
    keyword_queries = related_queries.get(cleaned_keyword) if related_queries else None
    rising_topics = keyword_queries.get("rising") if keyword_queries else None

    if rising_topics is None or rising_topics.empty:
        return []

    return rising_topics.head(top_n)["query"].tolist()
