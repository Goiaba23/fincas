from app.schemas.financial import Rule502020Request, Rule502020Response


def calculate_rule_50_30_20(req: Rule502020Request) -> Rule502020Response:
    income = req.monthly_income

    return Rule502020Response(
        needs=round(income * 0.50, 2),
        wants=round(income * 0.30, 2),
        savings=round(income * 0.20, 2),
        needs_percent=50.0,
        wants_percent=30.0,
        savings_percent=20.0,
    )
