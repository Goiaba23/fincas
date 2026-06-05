import httpx
from app.core.config import get_settings
from app.providers.bank import BankProvider, AccountData, TransactionData, ConnectionData

settings = get_settings()

PLUGGY_API = "https://api.pluggy.ai"


class PluggyProvider(BankProvider):
    def __init__(self):
        self._api_key: str | None = None
        self._client_id = settings.pluggy_client_id
        self._client_secret = settings.pluggy_client_secret

    async def _ensure_auth(self):
        if not self._api_key:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    f"{PLUGGY_API}/auth",
                    json={
                        "clientId": self._client_id,
                        "clientSecret": self._client_secret,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                self._api_key = data.get("apiKey")

    async def _headers(self):
        await self._ensure_auth()
        return {"X-API-KEY": self._api_key}

    async def create_connect_token(self, user_id: str) -> str:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{PLUGGY_API}/connect_token",
                headers=await self._headers(),
                json={},
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("accessToken")

    async def process_callback(self, item_id: str) -> ConnectionData:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{PLUGGY_API}/items/{item_id}",
                headers=await self._headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            return ConnectionData(item_id=data["id"], status=data.get("status", "connected"))

    async def get_accounts(self, item_id: str) -> list[AccountData]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{PLUGGY_API}/accounts",
                headers=await self._headers(),
                params={"itemId": item_id},
            )
            resp.raise_for_status()
            data = resp.json()
            accounts = []
            for acc in data.get("results", []):
                accounts.append(
                    AccountData(
                        external_id=acc["id"],
                        name=acc.get("name", ""),
                        type=acc.get("type", "BANK"),
                        balance=float(acc.get("balance", 0)),
                        currency_code=acc.get("currencyCode", "BRL"),
                        credit_limit=float(acc["creditLimit"]) if acc.get("creditLimit") else None,
                        card_brand=acc.get("cardBrand"),
                        card_last_digits=acc.get("cardLastDigits"),
                    )
                )
            return accounts

    async def get_transactions(self, account_id: str, days: int = 90) -> list[TransactionData]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{PLUGGY_API}/transactions",
                headers=await self._headers(),
                params={"accountId": account_id, "pageSize": 500},
            )
            resp.raise_for_status()
            data = resp.json()
            transactions = []
            for t in data.get("results", []):
                transactions.append(
                    TransactionData(
                        external_id=t["id"],
                        description=t.get("description", ""),
                        amount=float(t.get("amount", 0)),
                        date=t.get("date", ""),
                        category=t.get("category"),
                        type=t.get("type", "DEBIT"),
                        merchant_name=t.get("merchant", {}).get("name") if t.get("merchant") else None,
                    )
                )
            return transactions

    async def refresh_connection(self, item_id: str) -> None:
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{PLUGGY_API}/items/{item_id}",
                headers=await self._headers(),
            )


# Registry
_providers: dict[str, BankProvider] = {}


def register_provider(name: str, provider: BankProvider):
    _providers[name] = provider


def get_provider(name: str) -> BankProvider:
    provider = _providers.get(name)
    if not provider:
        raise ValueError(f"Unknown provider: {name}")
    return provider


def init_providers():
    if settings.pluggy_client_id and settings.pluggy_client_secret:
        register_provider("pluggy", PluggyProvider())
