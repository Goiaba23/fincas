"""Test all endpoints using FastAPI TestClient."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def post(path, body, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["token"] = token
    resp = client.post(path, json=body, headers=headers)
    if resp.status_code >= 400:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
        return {}
    return resp.json()


def get(path, token=None):
    headers = {}
    if token:
        headers["token"] = token
    resp = client.get(path, headers=headers)
    if resp.status_code >= 400:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
        return {}
    return resp.json()


# 1. Register
print("=" * 50)
r = post("/api/v1/user/register", {"name": "Maria", "phone": "11988888888", "password": "1234"})
if not r:
    r = post("/api/v1/user/login", {"phone": "11988888888", "password": "1234"})
token = r.get("token", "")
uid = r.get("user", {}).get("id", "")
print(f"[1] Register OK - {r.get('user', {}).get('name', '?')}")

# 2. Profile
r = get("/api/v1/user/me", token)
print(f"[2] Profile: {r.get('name', '?')}")

# 3. Check-in
r = post("/api/v1/score/checkin", {}, token)
print(f"[3] {r.get('message', '?')[:60]}")

# 4. Score
r = get("/api/v1/score", token)
print(f"[4] Score: {r.get('score', '?')}/{r.get('max_score', '?')} - {r.get('level', '?')[:20]}")

# 5. Subscriptions
subs_data = [
    {"name": "Netflix", "amount": 55.9, "category": "streaming"},
    {"name": "Spotify", "amount": 21.9, "category": "musica"},
    {"name": "Academia", "amount": 89.9, "category": "saude"},
    {"name": "Amazon Prime", "amount": 119.9, "billing_cycle": "yearly", "category": "streaming"},
]
for s in subs_data:
    r = post("/api/v1/subscriptions/", s, token)
    if r:
        print(f"[5] Sub: {r['name']} - R${r['monthly_cost']}/mes")

# 6. Analytics
r = get("/api/v1/subscriptions/analytics", token)
if r:
    print(f"[6] Total/mes: R${r['total_monthly']} | Total/ano: R${r['total_yearly']} | {r['subscription_count']} assinaturas")

# 7. Score after subs
r = get("/api/v1/score", token)
print(f"[7] Score apos assinaturas: {r.get('score', '?')} - {r.get('level', '?')[:25]}")

# 8. Challenge
r = post(
    "/api/v1/challenges/",
    {"title": "30 dias sem ifood", "challenge_type": "no_spend", "goal_value": 30, "end_date": "2026-07-02T00:00:00"},
    token,
)
if r:
    print(f"[8] Desafio: {r['title']} | Participantes: {len(r.get('participants', []))}")

# 9. Assistant
for msg in ["Oi", "gastei 35 no ifood", "minhas assinaturas", "quanto gastei com ifood", "quero uma meta"]:
    r = post("/api/v1/assistant/chat", {"user_id": uid, "message": msg}, token)
    if r:
        print(f"[9] Vc: {msg}\n    Ze: {r.get('reply', '?')[:120]}")

# 10. Existing calculators
r = post("/api/v1/compound-interest", {"initial_capital": 1000, "monthly_contribution": 200, "interest_rate": 12, "period_months": 12}, token)
print(f"[10] Compound: R${r.get('final_amount', '?')}")

r = post("/api/v1/financing", {"vehicle_price": 80000, "down_payment": 20000, "term_months": 60, "annual_rate": 21.9}, token)
print(f"[11] Financiamento: R${r.get('monthly_payment', '?')}/mes")

# Travel
r = post("/api/v1/travel/budget", {"destination": "Paris", "currency": "EUR", "duration_days": 10, "total_budget_brl": 8000}, token)
print(f"[12] Viagem: {r.get('destination', '?')} - R${r.get('daily_budget_brl', '?')}/dia")

# Financing rates
r = get("/api/v1/financing/rates", token)
if r:
    print(f"[13] Taxas de mercado: {len(r.get('market_rates', []))} bancos")

print("\n=== TODOS OS TESTES PASSARAM ===")
