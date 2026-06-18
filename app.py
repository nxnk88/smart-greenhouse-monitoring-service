import json
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="smart-greenhouse-monitoring-service",
    description=(
        "Учебный сервис мониторинга микроклимата умных теплиц. "
        "Выполнил: Копань Артем Алексеевич."
    ),
    version="2.0.0",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


greenhouses_data = [
    {
        "greenhouse_id": "gh-tomato-01",
        "name": "Томатная линия №1",
        "zone": "Северный сектор",
        "crop": "Томаты",
        "temperature_c": 24.6,
        "humidity_pct": 68,
        "soil_moisture_pct": 57,
        "co2_ppm": 840,
        "irrigation_enabled": True,
    },
    {
        "greenhouse_id": "gh-cucumber-02",
        "name": "Огуречная линия №2",
        "zone": "Северный сектор",
        "crop": "Огурцы",
        "temperature_c": 26.1,
        "humidity_pct": 74,
        "soil_moisture_pct": 63,
        "co2_ppm": 920,
        "irrigation_enabled": True,
    },
    {
        "greenhouse_id": "gh-herbs-03",
        "name": "Зелёный модуль",
        "zone": "Лабораторный сектор",
        "crop": "Пряные травы",
        "temperature_c": 17.2,
        "humidity_pct": 52,
        "soil_moisture_pct": 38,
        "co2_ppm": 760,
        "irrigation_enabled": True,
    },
    {
        "greenhouse_id": "gh-pepper-04",
        "name": "Перечная линия",
        "zone": "Южный сектор",
        "crop": "Сладкий перец",
        "temperature_c": 25.3,
        "humidity_pct": 64,
        "soil_moisture_pct": 51,
        "co2_ppm": 1010,
        "irrigation_enabled": True,
    },
    {
        "greenhouse_id": "gh-strawberry-05",
        "name": "Ягодный модуль",
        "zone": "Южный сектор",
        "crop": "Клубника",
        "temperature_c": 29.4,
        "humidity_pct": 83,
        "soil_moisture_pct": 79,
        "co2_ppm": 1320,
        "irrigation_enabled": False,
    },
    {
        "greenhouse_id": "gh-lettuce-06",
        "name": "Салатная линия",
        "zone": "Лабораторный сектор",
        "crop": "Листовой салат",
        "temperature_c": 21.8,
        "humidity_pct": 71,
        "soil_moisture_pct": 66,
        "co2_ppm": 690,
        "irrigation_enabled": True,
    },
    {
        "greenhouse_id": "gh-flowers-07",
        "name": "Цветочный модуль",
        "zone": "Западный сектор",
        "crop": "Декоративные цветы",
        "temperature_c": 23.5,
        "humidity_pct": 58,
        "soil_moisture_pct": 46,
        "co2_ppm": 880,
        "irrigation_enabled": True,
    },
    {
        "greenhouse_id": "gh-seedlings-08",
        "name": "Рассадное отделение",
        "zone": "Западный сектор",
        "crop": "Рассада",
        "temperature_c": 22.9,
        "humidity_pct": 62,
        "soil_moisture_pct": 43,
        "co2_ppm": 1180,
        "irrigation_enabled": False,
    },
]

greenhouses_df = pd.DataFrame(greenhouses_data)


def optimal_mask(dataframe: pd.DataFrame) -> pd.Series:
    """Return a boolean mask for greenhouses with a healthy microclimate."""
    return (
        dataframe["temperature_c"].between(18, 28)
        & dataframe["humidity_pct"].between(55, 80)
        & dataframe["soil_moisture_pct"].between(40, 75)
        & (dataframe["co2_ppm"] <= 1200)
        & dataframe["irrigation_enabled"]
    )


def dataframe_to_records(dataframe: pd.DataFrame) -> list[dict]:
    """Convert pandas values into JSON-native Python types."""
    return json.loads(dataframe.to_json(orient="records", force_ascii=False))


def greenhouse_records(dataframe: pd.DataFrame) -> list[dict]:
    enriched = dataframe.copy()
    enriched["status"] = optimal_mask(enriched).map(
        {True: "optimal", False: "attention"}
    )
    return dataframe_to_records(enriched)


@app.get("/", include_in_schema=False)
def dashboard() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api")
def api_info() -> dict:
    return {
        "service": "smart-greenhouse-monitoring-service",
        "message": "Мониторинг микроклимата и состояния умных теплиц",
        "author": "Копань Артем Алексеевич",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/greenhouses")
def get_greenhouses(
    zone: Optional[str] = Query(default=None, description="Фильтр по сектору"),
    crop: Optional[str] = Query(default=None, description="Фильтр по культуре"),
) -> dict:
    filtered = greenhouses_df

    if zone is not None:
        filtered = filtered[filtered["zone"].str.casefold() == zone.casefold()]
    if crop is not None:
        filtered = filtered[filtered["crop"].str.casefold() == crop.casefold()]

    return {"count": len(filtered), "greenhouses": greenhouse_records(filtered)}


@app.get("/greenhouse/{greenhouse_id}")
def get_greenhouse(greenhouse_id: str) -> dict:
    greenhouse = greenhouses_df[
        greenhouses_df["greenhouse_id"].str.casefold() == greenhouse_id.casefold()
    ]

    if greenhouse.empty:
        raise HTTPException(status_code=404, detail="Greenhouse not found")

    return greenhouse_records(greenhouse)[0]


@app.get("/optimal-greenhouses")
def get_optimal_greenhouses() -> dict:
    optimal = greenhouses_df[optimal_mask(greenhouses_df)]
    zone_distribution = optimal["zone"].value_counts().sort_index().to_dict()

    return {
        "message": "Параметры микроклимата находятся в рабочем диапазоне",
        "total_optimal_greenhouses": len(optimal),
        "zone_distribution": zone_distribution,
        "greenhouses": greenhouse_records(optimal),
    }


@app.get("/summary")
def get_summary() -> dict:
    optimal_count = int(optimal_mask(greenhouses_df).sum())
    total_count = len(greenhouses_df)

    return {
        "total_greenhouses": total_count,
        "optimal_greenhouses": optimal_count,
        "attention_required": total_count - optimal_count,
        "average_temperature_c": round(
            float(greenhouses_df["temperature_c"].mean()), 1
        ),
        "average_humidity_pct": round(
            float(greenhouses_df["humidity_pct"].mean()), 1
        ),
    }

