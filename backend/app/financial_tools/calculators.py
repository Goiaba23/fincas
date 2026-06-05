import math


def compound_interest(principal: float, rate: float, periods: int) -> dict:
    amount = principal * (1 + rate) ** periods
    earnings = amount - principal
    return {
        "principal": round(principal, 2),
        "rate_pct": round(rate * 100, 2),
        "periods": periods,
        "final_amount": round(amount, 2),
        "earnings": round(earnings, 2),
    }


def monthly_investment(monthly: float, rate: float, months: int) -> dict:
    if rate == 0:
        total = monthly * months
        return {"total_invested": round(total, 2), "final_amount": round(total, 2), "earnings": 0}
    amount = monthly * (((1 + rate) ** months - 1) / rate)
    total_invested = monthly * months
    return {
        "monthly": round(monthly, 2),
        "rate_pct": round(rate * 100, 2),
        "months": months,
        "total_invested": round(total_invested, 2),
        "final_amount": round(amount, 2),
        "earnings": round(amount - total_invested, 2),
    }


def fire_calculation(current_savings: float, monthly_savings: float, annual_return: float,
                     monthly_expenses: float) -> dict:
    monthly_return = annual_return / 12
    fire_number = monthly_expenses * 12 * 25  # 4% rule
    months_to_fire = 0
    accumulated = current_savings

    if monthly_savings > 0 and monthly_return > 0:
        while accumulated < fire_number and months_to_fire < 1200:
            accumulated = accumulated * (1 + monthly_return) + monthly_savings
            months_to_fire += 1
    elif monthly_savings > 0:
        months_to_fire = (fire_number - current_savings) / monthly_savings if monthly_savings > 0 else 0

    years = months_to_fire / 12
    return {
        "fire_number": round(fire_number, 2),
        "months_to_fire": round(months_to_fire),
        "years_to_fire": round(years, 1),
        "target_withdrawal_monthly": round(monthly_expenses, 2),
        "target_withdrawal_yearly": round(monthly_expenses * 12, 2),
        "current_savings": round(current_savings, 2),
        "monthly_savings": round(monthly_savings, 2),
    }


def loan_amortization_sac(principal: float, annual_rate: float, months: int) -> dict:
    monthly_rate = annual_rate / 12
    amortization = principal / months
    schedule = []
    remaining = principal
    total_interest = 0

    for i in range(1, months + 1):
        interest = remaining * monthly_rate
        payment = amortization + interest
        total_interest += interest
        schedule.append({
            "month": i,
            "payment": round(payment, 2),
            "amortization": round(amortization, 2),
            "interest": round(interest, 2),
            "remaining": round(remaining - amortization, 2),
        })
        remaining -= amortization

    return {
        "principal": round(principal, 2),
        "annual_rate_pct": round(annual_rate * 100, 2),
        "months": months,
        "total_paid": round(principal + total_interest, 2),
        "total_interest": round(total_interest, 2),
        "first_payment": round(schedule[0]["payment"], 2) if schedule else 0,
        "last_payment": round(schedule[-1]["payment"], 2) if schedule else 0,
        "schedule": schedule[:12],  # first 12 months
    }


def loan_amortization_price(principal: float, annual_rate: float, months: int) -> dict:
    monthly_rate = annual_rate / 12
    payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    schedule = []
    remaining = principal
    total_interest = 0

    for i in range(1, months + 1):
        interest = remaining * monthly_rate
        amortization = payment - interest
        total_interest += interest
        schedule.append({
            "month": i,
            "payment": round(payment, 2),
            "amortization": round(amortization, 2),
            "interest": round(interest, 2),
            "remaining": round(remaining - amortization, 2),
        })
        remaining -= amortization

    return {
        "principal": round(principal, 2),
        "annual_rate_pct": round(annual_rate * 100, 2),
        "months": months,
        "monthly_payment": round(payment, 2),
        "total_paid": round(payment * months, 2),
        "total_interest": round(total_interest, 2),
        "schedule": schedule[:12],
    }


def emergency_fund_target(monthly_expenses: float, months: int = 6) -> dict:
    return {
        "monthly_expenses": round(monthly_expenses, 2),
        "target_months": months,
        "target_amount": round(monthly_expenses * months, 2),
    }
