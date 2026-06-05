from app.schemas.financial import DebtPaymentRequest, DebtPaymentResponse
from app.services.debt_base import simulate_debt_payment


def calculate_avalanche(req: DebtPaymentRequest) -> DebtPaymentResponse:
    debts = sorted(
        (debt.model_copy() for debt in req.debts),
        key=lambda d: d.interest_rate,
        reverse=True,
    )
    return simulate_debt_payment(debts, req.extra_payment, "avalanche")
