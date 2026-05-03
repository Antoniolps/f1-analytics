from abc import ABC, abstractmethod


class QualifyingResultRepository(ABC):
    @abstractmethod
    def get_official_qualifying(self, year: int, round_number: int) -> list[str] | None:
        """Returns drivers ordered by official Q result, or None if Q hasn't run yet."""
