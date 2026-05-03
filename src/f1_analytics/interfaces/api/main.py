from fastapi import FastAPI

from f1_analytics.interfaces.api.routes import predictions, race_predictions

app = FastAPI(title="F1 Qualifying Prediction Engine")
app.include_router(predictions.router)
app.include_router(race_predictions.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
