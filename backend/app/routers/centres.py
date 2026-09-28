from decimal import Decimal
import json

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.exceptions import not_found
from app.core.redis import cache_service
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.test import DiagnosticTest
from app.schemas.centre import (
    CategoryListResponse,
    CategoryOut,
    CentreListResponse,
    CentreOut,
)

router = APIRouter(prefix="/centres", tags=["Diagnostic Centres"])

SERVICE_CATEGORIES = [
    "Cardiology",
    "Blood Test",
    "MRI Scan",
    "CT Scan",
    "Ultrasound",
    "X-Ray",
    "Neurology",
    "Full Body Checkup",
]


def _min_price_subquery():
    return (
        select(func.min(DiagnosticTest.price))
        .where(DiagnosticTest.centre_id == DiagnosticCentre.id)
        .correlate(DiagnosticCentre)
        .scalar_subquery()
    )


def _to_out(centre: DiagnosticCentre, test_count: int) -> CentreOut:
    data = CentreOut.model_validate(centre)
    return data.model_copy(update={"available_tests": test_count})


def _build_cache_key(prefix: str, **params) -> str:
    sorted_params = sorted((k, v) for k, v in params.items() if v is not None)
    param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
    return f"{prefix}:{param_str}"


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories(
    db: Session = Depends(get_db),
) -> CategoryListResponse:
    cache_key = "centres:categories"
    settings = get_settings()

    if settings.CACHE_ENABLED:
        cached = await cache_service.get(cache_key)
        if cached:
            return CategoryListResponse.model_validate_json(cached)

    rows = (
        db.query(
            DiagnosticTest.category.label("category"),
            func.count(DiagnosticTest.id).label("test_count"),
            func.count(func.distinct(DiagnosticTest.centre_id)).label("centre_count"),
            func.min(DiagnosticTest.price).label("min_price"),
            func.max(DiagnosticTest.price).label("max_price"),
        )
        .group_by(DiagnosticTest.category)
        .all()
    )
    stats = {row.category: row for row in rows}

    items: list[CategoryOut] = []
    for name in SERVICE_CATEGORIES:
        row = stats.get(name)
        if row is None:
            continue
        items.append(
            CategoryOut(
                id=name,
                name=name,
                centre_count=int(row.centre_count or 0),
                test_count=int(row.test_count or 0),
                min_price=float(row.min_price) if row.min_price is not None else None,
                max_price=float(row.max_price) if row.max_price is not None else None,
            )
        )

    for name, row in stats.items():
        if name in SERVICE_CATEGORIES:
            continue
        items.append(
            CategoryOut(
                id=name,
                name=name,
                centre_count=int(row.centre_count or 0),
                test_count=int(row.test_count or 0),
                min_price=float(row.min_price) if row.min_price is not None else None,
                max_price=float(row.max_price) if row.max_price is not None else None,
            )
        )

    response = CategoryListResponse(items=items)

    if settings.CACHE_ENABLED:
        await cache_service.set(cache_key, response.model_dump_json(), settings.CACHE_TTL_SECONDS)

    return response


@router.get("/meta/cities", response_model=list[str])
async def list_cities(
    db: Session = Depends(get_db),
) -> list[str]:
    cache_key = "centres:cities"
    settings = get_settings()

    if settings.CACHE_ENABLED:
        cached = await cache_service.get(cache_key)
        if cached:
            return json.loads(cached)

    rows = (
        db.query(DiagnosticCentre.city)
        .filter(DiagnosticCentre.city.isnot(None))
        .distinct()
        .order_by(DiagnosticCentre.city.asc())
        .all()
    )
    cities = [row[0] for row in rows if row[0]]

    if settings.CACHE_ENABLED:
        await cache_service.set(cache_key, json.dumps(cities), settings.CACHE_TTL_SECONDS)

    return cities


@router.get("/", response_model=CentreListResponse)
async def list_centres(
    request: Request,
    q: str | None = Query(default=None, description="Search by centre name, address or location"),
    location: str | None = Query(default=None, description="Filter by city or location"),
    category: str | None = Query(default=None, description="Filter by service or test category"),
    centre_type: str | None = Query(default=None, description="Hospital, Clinic or Diagnostic Center"),
    panel: str | None = Query(default=None, description="CGHS, ECHS or Corporate empanelment"),
    min_rating: Decimal | None = Query(default=None, ge=0, le=5),
    max_price: Decimal | None = Query(default=None, ge=0),
    open_now: bool | None = Query(default=None),
    sort: str = Query(default="relevance"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> CentreListResponse:
    settings = get_settings()

    if settings.CACHE_ENABLED and request.client:
        cache_key = _build_cache_key(
            "centres:list",
            q=q,
            location=location,
            category=category,
            centre_type=centre_type,
            panel=panel,
            min_rating=str(min_rating) if min_rating else None,
            max_price=str(max_price) if max_price else None,
            open_now=str(open_now) if open_now else None,
            sort=sort,
            page=page,
            page_size=page_size,
        )
        cached = await cache_service.get(cache_key)
        if cached:
            return CentreListResponse.model_validate_json(cached)

    query = db.query(DiagnosticCentre)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (DiagnosticCentre.name.ilike(like))
            | (DiagnosticCentre.location.ilike(like))
            | (func.coalesce(DiagnosticCentre.city, "").ilike(like))
        )
    if location:
        query = query.filter(
            (DiagnosticCentre.location.ilike(f"%{location.strip()}%"))
            | (func.coalesce(DiagnosticCentre.city, "").ilike(f"%{location.strip()}%"))
        )
    if centre_type and centre_type.strip().lower() not in ("all", "all types"):
        query = query.filter(DiagnosticCentre.centre_type.ilike(f"%{centre_type.strip()}%"))
    if panel and panel.strip().lower() not in ("all", "all panels"):
        query = query.filter(func.coalesce(DiagnosticCentre.panels, "").ilike(f"%{panel.strip()}%"))
    if min_rating is not None:
        query = query.filter(DiagnosticCentre.rating >= min_rating)
    if open_now is not None:
        query = query.filter(DiagnosticCentre.is_open_now == open_now)

    price_query = None
    if category and category.strip().lower() not in ("all", "all services"):
        cat_like = f"%{category.strip()}%"
        query = query.join(DiagnosticTest).filter(
            (DiagnosticTest.category.ilike(cat_like))
            | (DiagnosticTest.name.ilike(cat_like))
        ).distinct()
        price_query = (
            db.query(func.min(DiagnosticTest.price))
            .filter(
                DiagnosticTest.centre_id == DiagnosticCentre.id,
                (DiagnosticTest.category.ilike(cat_like))
                | (DiagnosticTest.name.ilike(cat_like)),
            )
            .correlate(DiagnosticCentre)
            .scalar_subquery()
        )
    if max_price is not None:
        if price_query is None:
            price_query = db.query(func.min(DiagnosticTest.price)).filter(
                DiagnosticTest.centre_id == DiagnosticCentre.id
            ).correlate(DiagnosticCentre).scalar_subquery()
        query = query.filter(price_query <= max_price)

    sort_key = (sort or "relevance").strip().lower()
    if sort_key == "price_low":
        price_expr = price_query if price_query is not None else _min_price_subquery()
        query = query.order_by(price_expr.asc().nulls_last(), DiagnosticCentre.name.asc())
    elif sort_key == "price_high":
        price_expr = price_query if price_query is not None else _min_price_subquery()
        query = query.order_by(price_expr.desc().nulls_last(), DiagnosticCentre.name.asc())
    elif sort_key == "name":
        query = query.order_by(DiagnosticCentre.name.asc())
    else:
        query = query.order_by(
            DiagnosticCentre.rating.desc().nulls_last(), DiagnosticCentre.name.asc()
        )

    total = query.count()
    centres = query.offset((page - 1) * page_size).limit(page_size).all()

    counts = dict(
        db.query(DiagnosticTest.centre_id, func.count(DiagnosticTest.id))
        .group_by(DiagnosticTest.centre_id)
        .all()
    )
    items = [_to_out(centre, counts.get(centre.id, 0)) for centre in centres]
    response = CentreListResponse(items=items, total=total, page=page, page_size=page_size)

    if settings.CACHE_ENABLED and request.client:
        await cache_service.set(cache_key, response.model_dump_json(), settings.CACHE_TTL_SECONDS)

    return response


@router.get("/{centre_id}", response_model=CentreOut)
async def get_centre(
    centre_id: int,
    db: Session = Depends(get_db),
) -> CentreOut:
    settings = get_settings()
    cache_key = f"centre:{centre_id}"

    if settings.CACHE_ENABLED:
        cached = await cache_service.get(cache_key)
        if cached:
            return CentreOut.model_validate_json(cached)

    centre = db.get(DiagnosticCentre, centre_id)
    if centre is None:
        raise not_found("Diagnostic centre not found")
    test_count = db.query(func.count(DiagnosticTest.id)).filter(DiagnosticTest.centre_id == centre_id).scalar()
    response = _to_out(centre, int(test_count or 0))

    if settings.CACHE_ENABLED:
        await cache_service.set(cache_key, response.model_dump_json(), settings.CACHE_TTL_SECONDS)

    return response