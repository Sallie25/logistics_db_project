from decimal import Decimal

from logistics_db.database import Session
from logistics_db.models import ExchangeRates


def seed_exchange_rates():
    session = Session()

    rates = [
        ExchangeRates(currency_code="USD", rate_to_ngn=Decimal("1500.00")),
        ExchangeRates(currency_code="EUR", rate_to_ngn=Decimal("1620.00")),
        ExchangeRates(currency_code="GBP", rate_to_ngn=Decimal("1900.00")),
        ExchangeRates(currency_code="NGN", rate_to_ngn=Decimal("1.00")),
    ]

    for rate in rates:
        session.merge(rate) 

    session.commit()
    session.close()
    print(f"Seeded {len(rates)} exchange rates")


if __name__ == "__main__":
    seed_exchange_rates()