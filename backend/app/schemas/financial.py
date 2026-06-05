from pydantic import BaseModel, Field
from typing import List, Optional


class CompoundInterestRequest(BaseModel):
    initial_capital: float = Field(gt=0, description="Initial capital (C)")
    monthly_contribution: float = Field(ge=0, description="Monthly contribution added each period")
    interest_rate: float = Field(gt=0, description="Annual interest rate in % (e.g. 12 for 12% a.a.)")
    period_months: int = Field(gt=0, le=1200, description="Investment period in months")


class MonthlyBreakdown(BaseModel):
    month: int
    initial_balance: float
    contribution: float
    interest_earned: float
    final_balance: float


class CompoundInterestResponse(BaseModel):
    final_amount: float
    total_contributions: float
    total_interest: float
    breakdown: List[MonthlyBreakdown]


class Rule502020Request(BaseModel):
    monthly_income: float = Field(gt=0, description="Monthly net income")


class Rule502020Response(BaseModel):
    needs: float
    wants: float
    savings: float
    needs_percent: float
    wants_percent: float
    savings_percent: float


class Rule72Request(BaseModel):
    rate: Optional[float] = Field(default=None, gt=0, description="Annual interest rate in %")
    years_to_double: Optional[float] = Field(default=None, gt=0, description="Years to double the investment")


class Rule72Response(BaseModel):
    rate: Optional[float]
    years_to_double: Optional[float]


class Debt(BaseModel):
    name: str
    balance: float = Field(gt=0)
    interest_rate: float = Field(ge=0, description="Annual interest rate in %")
    minimum_payment: float = Field(gt=0)


class DebtPaymentRequest(BaseModel):
    debts: List[Debt] = Field(min_length=1, max_length=50)
    extra_payment: float = Field(ge=0, description="Extra monthly payment beyond minimums")


class DebtPaymentStep(BaseModel):
    month: int
    debt_name: str
    payment: float
    remaining_balance: float


class DebtResult(BaseModel):
    name: str
    initial_balance: float
    interest_rate: float
    total_paid: float
    months_to_payoff: int


class DebtPaymentResponse(BaseModel):
    strategy: str
    total_months: int
    total_interest_paid: float
    total_paid: float
    payoff_order: List[str]
    debt_results: List[DebtResult]
    monthly_steps: List[DebtPaymentStep]


class FinancingRequest(BaseModel):
    vehicle_price: float = Field(gt=0, description="Vehicle price in R$")
    down_payment: float = Field(ge=0, description="Down payment in R$")
    term_months: int = Field(gt=0, le=120, description="Financing term in months")
    annual_rate: Optional[float] = Field(default=None, ge=0, description="Annual interest rate in %. If null, uses market average")


class AmortizationRow(BaseModel):
    month: int
    outstanding_balance: float
    payment: float
    interest: float
    principal: float


class BankRate(BaseModel):
    bank_name: str
    product: str
    annual_rate: float
    monthly_rate: float
    source: str
    updated_at: str


class FinancingResponse(BaseModel):
    financed_amount: float
    down_payment: float
    term_months: int
    annual_rate: float
    monthly_payment: float
    total_payment: float
    total_interest: float
    vehicle_price: float
    amortization_schedule: List[AmortizationRow]
    market_rates: List[BankRate]


class TravelBudgetRequest(BaseModel):
    destination: str
    currency: str = Field(default="BRL", description="Local currency code")
    duration_days: int = Field(gt=0, le=365)
    total_budget_brl: float = Field(gt=0, description="Total budget in R$")
    accommodation_share: float = Field(default=0.40, ge=0, le=1)
    food_share: float = Field(default=0.25, ge=0, le=1)
    transport_share: float = Field(default=0.15, ge=0, le=1)
    leisure_share: float = Field(default=0.12, ge=0, le=1)
    emergencies_share: float = Field(default=0.08, ge=0, le=1)


class TravelCategoryBudget(BaseModel):
    category: str
    total: float
    daily: float
    percent: float


class TravelBudgetResponse(BaseModel):
    destination: str
    duration_days: int
    total_budget_brl: float
    daily_budget_brl: float
    currency: str
    categories: List[TravelCategoryBudget]
    saving_goal_per_day: float
    days_to_save: int


class TravelExpenseRequest(BaseModel):
    daily_budget: float = Field(gt=0)
    expenses: List[float] = Field(min_length=1)


class TravelExpenseResponse(BaseModel):
    daily_budget: float
    total_spent: float
    remaining: float
    status: str  # "dentro", "atencao", "estourou"
    percent_used: float


class CurrencyRate(BaseModel):
    from_currency: str
    to_currency: str
    rate: float
    updated_at: str
