from datetime import datetime
from app.schemas.financial import (
    FinancingRequest,
    FinancingResponse,
    AmortizationRow,
    BankRate,
)

MARKET_RATES = [
    BankRate(bank_name="Banco do Brasil", product="CDC Auto", annual_rate=21.90, monthly_rate=1.66, source="bb.com.br", updated_at="2026-06"),
    BankRate(bank_name="Caixa Econômica Federal", product="CDC Auto", annual_rate=22.50, monthly_rate=1.71, source="caixa.gov.br", updated_at="2026-06"),
    BankRate(bank_name="Itaú", product="Financiamento Auto", annual_rate=23.40, monthly_rate=1.77, source="itau.com.br", updated_at="2026-06"),
    BankRate(bank_name="Bradesco", product="CDC Auto", annual_rate=24.10, monthly_rate=1.82, source="bradesco.com.br", updated_at="2026-06"),
    BankRate(bank_name="Santander", product="Financiamento Auto", annual_rate=24.90, monthly_rate=1.88, source="santander.com.br", updated_at="2026-06"),
    BankRate(bank_name="Nubank", product="Empréstimo Pessoal", annual_rate=19.90, monthly_rate=1.53, source="nubank.com.br", updated_at="2026-06"),
    BankRate(bank_name="C6 Bank", product="CDC Auto", annual_rate=21.50, monthly_rate=1.64, source="c6bank.com.br", updated_at="2026-06"),
    BankRate(bank_name="Inter", product="Financiamento Auto", annual_rate=20.90, monthly_rate=1.59, source="bancointer.com.br", updated_at="2026-06"),
    BankRate(bank_name="BV", product="Financiamento Auto", annual_rate=19.90, monthly_rate=1.53, source="bancobv.com.br", updated_at="2026-06"),
    BankRate(bank_name="Omni", product="CDC Auto", annual_rate=26.50, monthly_rate=1.98, source="omnibrasil.com.br", updated_at="2026-06"),
]


def calculate_financing(req: FinancingRequest) -> FinancingResponse:
    financed = req.vehicle_price - req.down_payment
    rate = req.annual_rate if req.annual_rate is not None else 21.90
    monthly_rate = (rate / 100) / 12
    n = req.term_months

    if monthly_rate == 0:
        pmt = financed / n
    else:
        pmt = financed * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)

    balance = financed
    total_interest = 0
    schedule = []

    for month in range(1, n + 1):
        interest = balance * monthly_rate
        principal = pmt - interest
        balance -= principal
        total_interest += interest

        schedule.append(AmortizationRow(
            month=month,
            outstanding_balance=round(max(balance, 0), 2),
            payment=round(pmt, 2),
            interest=round(interest, 2),
            principal=round(principal, 2),
        ))

    total_payment = round(pmt * n, 2)

    return FinancingResponse(
        financed_amount=round(financed, 2),
        down_payment=req.down_payment,
        term_months=n,
        annual_rate=rate,
        monthly_payment=round(pmt, 2),
        total_payment=total_payment,
        total_interest=round(total_interest, 2),
        vehicle_price=req.vehicle_price,
        amortization_schedule=schedule,
        market_rates=MARKET_RATES,
    )
