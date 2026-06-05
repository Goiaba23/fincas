from app.schemas.financial import CompoundInterestRequest, CompoundInterestResponse, MonthlyBreakdown


def calculate_compound_interest(req: CompoundInterestRequest) -> CompoundInterestResponse:
    monthly_rate = (req.interest_rate / 100) / 12

    balance = req.initial_capital
    total_contributions = 0
    breakdown = []

    for month in range(1, req.period_months + 1):
        initial_balance = round(balance, 2)
        interest_earned = round(balance * monthly_rate, 2)
        balance += interest_earned + req.monthly_contribution
        total_contributions += req.monthly_contribution

        breakdown.append(MonthlyBreakdown(
            month=month,
            initial_balance=initial_balance,
            contribution=req.monthly_contribution,
            interest_earned=interest_earned,
            final_balance=round(balance, 2),
        ))

    total_contributions += req.initial_capital
    total_interest = round(balance - total_contributions, 2)

    return CompoundInterestResponse(
        final_amount=round(balance, 2),
        total_contributions=round(total_contributions, 2),
        total_interest=total_interest,
        breakdown=breakdown,
    )
