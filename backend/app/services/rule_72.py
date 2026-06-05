from app.schemas.financial import Rule72Request, Rule72Response


def calculate_rule_72(req: Rule72Request) -> Rule72Response:
    if req.rate is not None:
        years = 72.0 / req.rate
        return Rule72Response(rate=req.rate, years_to_double=round(years, 2))
    elif req.years_to_double is not None:
        rate = 72.0 / req.years_to_double
        return Rule72Response(rate=round(rate, 2), years_to_double=req.years_to_double)
    else:
        raise ValueError("Either rate or years_to_double must be provided")
