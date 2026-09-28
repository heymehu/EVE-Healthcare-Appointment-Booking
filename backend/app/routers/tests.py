from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import not_found
from app.models.diagnostic_centre import DiagnosticCentre
from app.models.test import DiagnosticTest
from app.schemas.test import TestOut

centres_tests_router = APIRouter(prefix="/centres", tags=["Tests"])
tests_router = APIRouter(prefix="/tests", tags=["Tests"])


@centres_tests_router.get("/{centre_id}/tests", response_model=list[TestOut])
def list_centre_tests(centre_id: int, db: Session = Depends(get_db)) -> list[TestOut]:
    centre = db.get(DiagnosticCentre, centre_id)
    if centre is None:
        raise not_found("Diagnostic centre not found")
    tests = (
        db.query(DiagnosticTest)
        .filter(DiagnosticTest.centre_id == centre_id)
        .order_by(DiagnosticTest.price.asc())
        .all()
    )
    return [TestOut.model_validate(test) for test in tests]


@tests_router.get("/{test_id}", response_model=TestOut)
def get_test(test_id: int, db: Session = Depends(get_db)) -> TestOut:
    test = db.get(DiagnosticTest, test_id)
    if test is None:
        raise not_found("Diagnostic test not found")
    return TestOut.model_validate(test)
