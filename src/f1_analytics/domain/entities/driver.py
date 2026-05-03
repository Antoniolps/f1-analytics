from dataclasses import dataclass


@dataclass(frozen=True)
class Driver:
    code: str
    team: str
