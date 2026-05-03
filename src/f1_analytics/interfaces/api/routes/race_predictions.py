from fastapi import APIRouter, Depends

from f1_analytics.application.use_cases.predict_race import PredictRaceUseCase
from f1_analytics.composition import build_predict_race_use_case

router = APIRouter(prefix="/predictions/race", tags=["predictions"])

_use_case: PredictRaceUseCase | None = None


def get_use_case() -> PredictRaceUseCase:
    global _use_case
    if _use_case is None:
        _use_case = build_predict_race_use_case()
    return _use_case


@router.get("/{year}/{round_number}")
def predict_race(
    year: int,
    round_number: int,
    use_case: PredictRaceUseCase = Depends(get_use_case),
) -> dict:
    prediction = use_case.execute(year, round_number)
    return {
        "year": prediction.year,
        "round": prediction.round,
        "weekend": prediction.weekend_name,
        "signals_used": prediction.signals_used,
        "grid": [
            {
                "position": e.position,
                "driver": e.driver_code,
                "team": e.team,
                "score": e.score,
            }
            for e in prediction.grid
        ],
    }
