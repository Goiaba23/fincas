from app.schemas.financial import DebtPaymentRequest, DebtPaymentResponse
from app.services.debt_base import simulate_debt_payment


def calculate_snowball(req: DebtPaymentRequest) -> DebtPaymentResponse:
    debts = sorted(
        (debt.model_copy() for debt in req.debts),
        key=lambda d: d.balance,
    )
    return simulate_debt_payment(debts, req.extra_payment, "snowball")
