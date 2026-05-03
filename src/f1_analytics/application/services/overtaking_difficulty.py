from enum import Enum


class OvertakingDifficulty(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


_HIGH_KEYWORDS = {
    "monaco",
    "hungar",
    "singapore",
    "imola",
    "emilia",
    "miami",
    "zandvoort",
    "dutch",
    "barcelona",
    "spanish",
}

_LOW_KEYWORDS = {
    "monza",
    "italian",
    "spa",
    "belgian",
    "bahrain",
    "saudi",
    "jeddah",
    "azerbaijan",
    "baku",
    "chinese",
    "shanghai",
    "brazilian",
    "são paulo",
    "sao paulo",
    "interlagos",
}


def classify_event(event_name: str) -> OvertakingDifficulty:
    name = event_name.lower()
    if any(k in name for k in _HIGH_KEYWORDS):
        return OvertakingDifficulty.HIGH
    if any(k in name for k in _LOW_KEYWORDS):
        return OvertakingDifficulty.LOW
    return OvertakingDifficulty.MEDIUM
