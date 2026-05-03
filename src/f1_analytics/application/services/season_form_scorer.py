from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class RaceResult:
    round: int
    positions: dict[str, int]


class SeasonFormScorer:
    """Weighted average of finishing positions across prior races. More recent races weigh more."""

    def score(self, prior_results: list[RaceResult]) -> dict[str, float]:
        if not prior_results:
            return {}

        sorted_results = sorted(prior_results, key=lambda r: r.round)
        n = len(sorted_results)
        weighted: dict[str, float] = defaultdict(float)
        weights_sum: dict[str, float] = defaultdict(float)

        for idx, result in enumerate(sorted_results):
            recency_weight = 1.0 + idx / max(n - 1, 1)
            for driver, position in result.positions.items():
                weighted[driver] += position * recency_weight
                weights_sum[driver] += recency_weight

        return {driver: weighted[driver] / weights_sum[driver] for driver in weighted}
