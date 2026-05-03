class RelativeRanker:
    """Converts absolute pace per driver into delta vs the session's fastest."""

    def rank(self, pace: dict[str, float]) -> dict[str, float]:
        if not pace:
            return {}
        fastest = min(pace.values())
        return {driver: t - fastest for driver, t in pace.items()}
