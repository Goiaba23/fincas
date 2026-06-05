from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class AccountData:
    external_id: str
    name: str
    type: str
    balance: float
    currency_code: str
    credit_limit: float | None = None
    card_brand: str | None = None
    card_last_digits: str | None = None


@dataclass
class TransactionData:
    external_id: str
    description: str
    amount: float
    date: str
    category: str | None = None
    type: str = "DEBIT"
    installment_number: int | None = None
    total_installments: int | None = None
    merchant_name: str | None = None


@dataclass
class ConnectionData:
    item_id: str
    status: str


class BankProvider(ABC):
    """Abstract base for bank sync providers (Pluggy, Belvo, etc)."""

    @abstractmethod
    async def create_connect_token(self, user_id: str) -> str:
        ...

    @abstractmethod
    async def process_callback(self, item_id: str) -> ConnectionData:
        ...

    @abstractmethod
    async def get_accounts(self, item_id: str) -> list[AccountData]:
        ...

    @abstractmethod
    async def get_transactions(self, account_id: str, days: int = 90) -> list[TransactionData]:
        ...

    @abstractmethod
    async def refresh_connection(self, item_id: str) -> None:
        ...
