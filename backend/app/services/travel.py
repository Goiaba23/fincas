from app.schemas.financial import (
    TravelBudgetRequest,
    TravelBudgetResponse,
    TravelCategoryBudget,
    TravelExpenseRequest,
    TravelExpenseResponse,
)


def calculate_travel_budget(req: TravelBudgetRequest) -> TravelBudgetResponse:
    daily_total = req.total_budget_brl / req.duration_days

    categories = [
        TravelCategoryBudget(
            category="acomodacao",
            total=round(req.total_budget_brl * req.accommodation_share, 2),
            daily=round(daily_total * req.accommodation_share, 2),
            percent=round(req.accommodation_share * 100, 1),
        ),
        TravelCategoryBudget(
            category="alimentacao",
            total=round(req.total_budget_brl * req.food_share, 2),
            daily=round(daily_total * req.food_share, 2),
            percent=round(req.food_share * 100, 1),
        ),
        TravelCategoryBudget(
            category="transporte",
            total=round(req.total_budget_brl * req.transport_share, 2),
            daily=round(daily_total * req.transport_share, 2),
            percent=round(req.transport_share * 100, 1),
        ),
        TravelCategoryBudget(
            category="lazer",
            total=round(req.total_budget_brl * req.leisure_share, 2),
            daily=round(daily_total * req.leisure_share, 2),
            percent=round(req.leisure_share * 100, 1),
        ),
        TravelCategoryBudget(
            category="emergencias",
            total=round(req.total_budget_brl * req.emergencies_share, 2),
            daily=round(daily_total * req.emergencies_share, 2),
            percent=round(req.emergencies_share * 100, 1),
        ),
    ]

    saving_per_day = req.total_budget_brl / 30
    days_to_save = req.duration_days

    return TravelBudgetResponse(
        destination=req.destination,
        duration_days=req.duration_days,
        total_budget_brl=req.total_budget_brl,
        daily_budget_brl=round(daily_total, 2),
        currency=req.currency,
        categories=categories,
        saving_goal_per_day=round(saving_per_day, 2),
        days_to_save=days_to_save,
    )


def check_travel_expenses(req: TravelExpenseRequest) -> TravelExpenseResponse:
    total_spent = sum(req.expenses)
    remaining = req.daily_budget - total_spent
    percent_used = round((total_spent / req.daily_budget) * 100, 2)

    if percent_used <= 80:
        status = "dentro"
    elif percent_used <= 100:
        status = "atencao"
    else:
        status = "estourou"

    return TravelExpenseResponse(
        daily_budget=req.daily_budget,
        total_spent=round(total_spent, 2),
        remaining=round(remaining, 2),
        status=status,
        percent_used=percent_used,
    )
