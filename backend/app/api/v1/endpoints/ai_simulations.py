from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.financial_tools.calculators import (
    compound_interest,
    monthly_investment,
    fire_calculation,
    loan_amortization_sac,
    loan_amortization_price,
    emergency_fund_target,
)

router = APIRouter(prefix="/ai/simulate", tags=["ai"])


class CompoundRequest(BaseModel):
    principal: float
    annual_rate_pct: float
    years: int


class MonthlyInvestRequest(BaseModel):
    monthly: float
    annual_rate_pct: float
    years: int


class FIRERequest(BaseModel):
    current_savings: float
    monthly_savings: float
    annual_return_pct: float
    monthly_expenses: float


class LoanRequest(BaseModel):
    principal: float
    annual_rate_pct: float
    months: int


class EmergencyRequest(BaseModel):
    monthly_expenses: float
    months: int = 6


@router.post("/compound-interest")
async def simulate_compound(req: CompoundRequest):
    return compound_interest(req.principal, req.annual_rate_pct / 100, req.years)


@router.post("/monthly-investment")
async def simulate_monthly_investment(req: MonthlyInvestRequest):
    rate = req.annual_rate_pct / 100 / 12
    return monthly_investment(req.monthly, rate, req.years * 12)


@router.post("/fire")
async def simulate_fire(req: FIRERequest):
    return fire_calculation(
        req.current_savings,
        req.monthly_savings,
        req.annual_return_pct / 100,
        req.monthly_expenses,
    )


@router.post("/loan-sac")
async def simulate_sac(req: LoanRequest):
    return loan_amortization_sac(req.principal, req.annual_rate_pct / 100, req.months)


@router.post("/loan-price")
async def simulate_price(req: LoanRequest):
    return loan_amortization_price(req.principal, req.annual_rate_pct / 100, req.months)


@router.post("/emergency-fund")
async def simulate_emergency(req: EmergencyRequest):
    return emergency_fund_target(req.monthly_expenses, req.months)
