# f1-analytics

F1 Qualifying & Race Prediction Engine. Predicts qualifying grid and race results from in-weekend session data (FP1/FP2/FP3, Sprint Qualifying, Sprint) plus prior-rounds season form, sourced via [FastF1](https://docs.fastf1.dev/).

## Requirements

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) for dependency management

## Setup

```bash
uv sync
```

First run downloads FastF1 data into `./cache/`; subsequent runs are fast.

## Usage

### CLI

Predict qualifying:
```bash
uv run python -m f1_analytics.interfaces.cli.predict <year> <round> [--verbose]
```

Predict race:
```bash
uv run python -m f1_analytics.interfaces.cli.predict_race <year> <round> [--verbose]
```

Examples:
```bash
uv run python -m f1_analytics.interfaces.cli.predict 2026 3        # Japan GP qualifying
uv run python -m f1_analytics.interfaces.cli.predict_race 2026 4   # Miami GP race (sprint weekend)
```

### HTTP API

```bash
uv run uvicorn f1_analytics.interfaces.api.main:app --reload
```

Endpoints:
- `GET /predictions/{year}/{round_number}` — qualifying prediction
- `GET /predictions/race/{year}/{round_number}` — race prediction
- `GET /health`

## How predictions work

**Qualifying** — extracts the best clean lap per driver per practice session, computes pace deltas vs the fastest, then aggregates with format-aware weights:
- Conventional: FP1=0.20, FP2=0.30, FP3=0.50
- Sprint: FP1=0.20, SQ=0.70, S=0.10 (sprint race uses different setup, so it's downweighted)

**Race** — combines five rank-based signals via weighted average:
| Signal | Conventional | Sprint |
|---|---|---|
| `grid` (official Q if available, else predicted quali) | 0.40 | 0.35 |
| `race_pace` (long-run averages from practice/sprint) | 0.30 | 0.20 |
| `tire_deg` (linear-regression slope of lap_time vs tyre_life) | 0.20 | 0.15 |
| `sprint_result` | — | 0.20 |
| `season_form` (recency-weighted prior-rounds standings) | 0.10 | 0.10 |

The `signals_used` field on each `RacePrediction` records which signals contributed (e.g. `grid:official` vs `grid:predicted`).

## Architecture

Strict hexagonal / clean architecture under `src/f1_analytics/`. Dependencies point inward: `interfaces` → `application` → `domain`, with `infrastructure` plugged in at the edges. All wiring lives in `composition.py`.

```
src/f1_analytics/
├── domain/              # Pure entities & value objects, no I/O
├── application/
│   ├── ports/           # Repository interfaces
│   ├── services/        # Pace extraction, ranking, tire-deg, season-form, aggregators
│   └── use_cases/       # PredictQualifyingUseCase, PredictRaceUseCase
├── infrastructure/
│   └── fastf1/          # FastF1 adapters
├── interfaces/
│   ├── api/             # FastAPI app & routers
│   └── cli/             # argparse entry points
└── composition.py       # Dependency wiring
```

## Caching

FastF1's on-disk cache is enabled at `./cache/` (created automatically). It is the only persistence layer.
