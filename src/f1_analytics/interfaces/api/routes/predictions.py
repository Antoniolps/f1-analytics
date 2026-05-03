from fastapi import APIRouter, Depends

from f1_analytics.application.use_cases.predict_qualifying import PredictQualifyingUseCase
from f1_analytics.composition import build_predict_use_case

router = APIRouter(prefix="/predictions", tags=["predictions"])

_use_case: PredictQualifyingUseCase | None = None


def get_use_case() -> PredictQualifyingUseCase:
    global _use_case
    if _use_case is None:
        _use_case = build_predict_use_case()
    return _use_case


@router.get("/{year}/{round_number}")
def predict_qualifying(
    year: int,
    round_number: int,
    use_case: PredictQualifyingUseCase = Depends(get_use_case),
) -> dict:
    prediction = use_case.execute(year, round_number)
    return {
        "year": prediction.year,
        "round": prediction.round,
        "weekend": prediction.weekend_name,
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
