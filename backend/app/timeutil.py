from datetime import datetime, timezone


def utcnow() -> datetime:
    """Current UTC time as a naive datetime (all timestamps in the DB are UTC)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
