from enum import Enum


class SessionType(str, Enum):
    FP1 = "FP1"
    FP2 = "FP2"
    FP3 = "FP3"
    SPRINT_QUALIFYING = "SQ"
    SPRINT = "S"


class WeekendFormat(str, Enum):
    CONVENTIONAL = "conventional"
    SPRINT = "sprint"
