# app/routers/map.py (수정된 최종 코드)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import get_db
from pyproj import Transformer


transformer = Transformer.from_crs(
    "EPSG:5181",  # 또는 5179 / 실제 좌표계 확인
    "EPSG:4326",  # 위경도
    always_xy=True
)

# 🚨 수정: 라우터 변수 이름을 map_router로 변경합니다.
map_router = APIRouter(prefix="/map", tags=["Map"])

# 🚨 데코레이터도 map_router로 변경합니다.
@map_router.get("/hospitals")
def get_hospitals(
    db: Session = Depends(get_db),
    north: float = Query(None), # max_lat
    south: float = Query(None), # min_lat
    east: float = Query(None),  # max_lng
    west: float = Query(None)   # min_lng
):
    query_str = """
        SELECT
            name,
            y AS lat,
            x AS lng,
            address,
            tel,
            homepage
        FROM master_medical
        WHERE x IS NOT NULL
          AND y IS NOT NULL
    """
    params = {}
    
    if north is not None and south is not None and east is not None and west is not None:
        query_str += " AND y BETWEEN :south AND :north AND x BETWEEN :west AND :east"
        params = {"south": south, "north": north, "west": west, "east": east}
    
    # LIMIT to prevent overload
    query_str += " LIMIT 500"

    rows = db.execute(text(query_str), params).fetchall()

    return [
        {
            "name": r.name,
            "lat": float(r.lat),
            "lng": float(r.lng),
            "address": r.address,
            "tel": r.tel,
            "homepage": r.homepage if hasattr(r, 'homepage') else "",
        }
        for r in rows
    ]

@map_router.get("/convenience-stores")
def get_convenience_stores(db: Session = Depends(get_db)):
    # Convenience stores usually require transformation, so we verify size or just limit.
    # For now, adding a limit to be safe.
    rows = db.execute(text("""
        SELECT
            name,
            address,
            tel,
            x_coord,
            y_coord
        FROM safe_pharmacy
        WHERE x_coord IS NOT NULL
          AND y_coord IS NOT NULL
        LIMIT 200
    """)).fetchall()

    results = []
    for r in rows:
        try:
            lng, lat = transformer.transform(
                float(r.x_coord),
                float(r.y_coord)
            )

            results.append({
                "name": r.name,
                "lat": lat,
                "lng": lng,
                "address": r.address,
                "tel": r.tel,
            })
        except Exception:
            continue

    return results

@map_router.get("/pharmacies")
def get_pharmacies(
    db: Session = Depends(get_db),
    north: float = Query(None),
    south: float = Query(None),
    east: float = Query(None),
    west: float = Query(None)
):
    query_str = """
        SELECT
            `약국명`   AS name,
            `y`        AS lat,
            `x`        AS lng,
            `주소`     AS address,
            `전화번호` AS tel
        FROM pharmacy
        WHERE x IS NOT NULL
          AND y IS NOT NULL
    """
    params = {}

    if north is not None and south is not None and east is not None and west is not None:
        query_str += " AND y BETWEEN :south AND :north AND x BETWEEN :west AND :east"
        params = {"south": south, "north": north, "west": west, "east": east}
    
    query_str += " LIMIT 500"

    rows = db.execute(text(query_str), params).fetchall()

    return [
        {
            "name": r.name,
            "lat": float(r.lat),
            "lng": float(r.lng),
            "address": r.address,
            "tel": r.tel,
        }
        for r in rows
    ]