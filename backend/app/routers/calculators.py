from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.financial import (
    CompoundInterestRequest,
    CompoundInterestResponse,
    Rule502020Request,
    Rule502020Response,
    Rule72Request,
    Rule72Response,
    DebtPaymentRequest,
    DebtPaymentResponse,
    FinancingRequest,
    FinancingResponse,
    TravelBudgetRequest,
    TravelBudgetResponse,
    TravelExpenseRequest,
    TravelExpenseResponse,
    CurrencyRate,
)
from app.services.compound_interest import calculate_compound_interest
from app.services.rule_50_30_20 import calculate_rule_50_30_20
from app.services.rule_72 import calculate_rule_72
from app.services.snowball import calculate_snowball
from app.services.avalanche import calculate_avalanche
from app.services.financing import calculate_financing, MARKET_RATES
from app.services.travel import calculate_travel_budget, check_travel_expenses

router = APIRouter(prefix="/api/v1")


CURRENCY_RATES: dict[str, float] = {
    "USD": 5.25,
    "EUR": 5.70,
    "GBP": 6.70,
    "ARS": 0.014,
    "CLP": 0.0066,
    "UYU": 0.13,
    "MXN": 0.29,
    "COP": 0.0013,
    "JPY": 0.036,
    "AUD": 3.50,
    "CAD": 3.85,
}


@router.post("/compound-interest", response_model=CompoundInterestResponse)
def compound_interest(req: CompoundInterestRequest):
    return calculate_compound_interest(req)


@router.post("/rule-50-30-20", response_model=Rule502020Response)
def rule_50_30_20(req: Rule502020Request):
    return calculate_rule_50_30_20(req)


@router.post("/rule-72", response_model=Rule72Response)
def rule_72(req: Rule72Request):
    try:
        return calculate_rule_72(req)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/snowball", response_model=DebtPaymentResponse)
def snowball(req: DebtPaymentRequest):
    return calculate_snowball(req)


@router.post("/avalanche", response_model=DebtPaymentResponse)
def avalanche(req: DebtPaymentRequest):
    return calculate_avalanche(req)


@router.post("/financing", response_model=FinancingResponse)
def financing(req: FinancingRequest):
    return calculate_financing(req)


@router.get("/financing/rates")
def financing_rates():
    return {"market_rates": MARKET_RATES, "updated_at": datetime.now().isoformat()}


@router.post("/travel/budget", response_model=TravelBudgetResponse)
def travel_budget(req: TravelBudgetRequest):
    return calculate_travel_budget(req)


@router.post("/travel/expenses", response_model=TravelExpenseResponse)
def travel_expenses(req: TravelExpenseRequest):
    return check_travel_expenses(req)


@router.get("/travel/currencies")
def travel_currencies():
    return {"currencies": CURRENCY_RATES, "base": "BRL", "updated_at": datetime.now().isoformat()}


@router.post("/travel/convert")
def travel_convert(from_currency: str = "USD", amount: float = 100):
    rate = CURRENCY_RATES.get(from_currency.upper())
    if rate is None:
        raise HTTPException(status_code=404, detail=f"Currency {from_currency} not found")
    return {
        "from": from_currency.upper(),
        "to": "BRL",
        "amount": amount,
        "rate": rate,
        "converted": round(amount * rate, 2),
    }


@router.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
