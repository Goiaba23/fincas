from typing import Dict, List, Tuple
from app.schemas.financial import Debt, DebtPaymentRequest, DebtPaymentResponse, DebtResult, DebtPaymentStep


def simulate_debt_payment(
    debts: List[Debt],
    extra_payment: float,
    strategy: str,
) -> DebtPaymentResponse:
    monthly_rate = {d.name: (d.interest_rate / 100) / 12 for d in debts}
    remaining = {d.name: d.balance for d in debts}

    total_interest_paid = 0.0
    total_paid = 0.0
    month = 0
    monthly_steps = []
    payoff_order = []
    debt_results: Dict[str, dict] = {
        d.name: {"total_paid": 0.0, "months": 0}
        for d in debts
    }

    active = [d for d in debts]

    while active:
        month += 1
        primary = active[0]

        payment = primary.minimum_payment + extra_payment
        for d in active:
            if d.name != primary.name:
                payment += d.minimum_payment

        for d in active:
            interest = remaining[d.name] * monthly_rate[d.name]
            total_interest_paid += interest
            remaining[d.name] += interest

            alloc = min(payment if d.name == primary.name else d.minimum_payment, remaining[d.name])
            remaining[d.name] -= alloc
            total_paid += alloc
            debt_results[d.name]["total_paid"] += alloc

            monthly_steps.append(DebtPaymentStep(
                month=month,
                debt_name=d.name,
                payment=round(alloc, 2),
                remaining_balance=round(remaining[d.name], 2),
            ))

        newly_paid = [d for d in active if remaining[d.name] <= 0.01]
        for d in newly_paid:
            debt_results[d.name]["months"] = month
            payoff_order.append(d.name)
            leftover = abs(remaining[d.name])
            if leftover > 0 and len(active) > 1:
                remaining[active[1].name] -= leftover

        active = [d for d in active if remaining[d.name] > 0.01]

    return DebtPaymentResponse(
        strategy=strategy,
        total_months=month,
        total_interest_paid=round(total_interest_paid, 2),
        total_paid=round(total_paid, 2),
        payoff_order=payoff_order,
        debt_results=[
            DebtResult(
                name=d.name,
                initial_balance=d.balance,
                interest_rate=d.interest_rate,
                total_paid=round(debt_results[d.name]["total_paid"], 2),
                months_to_payoff=debt_results[d.name]["months"],
            ) for d in debts
        ],
        monthly_steps=monthly_steps,
    )
