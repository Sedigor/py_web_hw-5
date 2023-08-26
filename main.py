import argparse
import aiohttp
import asyncio
from datetime import datetime, timedelta

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

class ExchangeRateFetcher:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def fetch_exchange_rates(self, date):
        async with self.session.get(API_URL + date) as response:
            return await response.json()

    async def get_exchange_rates(self, start_date, days):
        tasks = []
        exchange_rates = []

        for day in range(days):
            date = (start_date - timedelta(days=day)).strftime("%d.%m.%Y")
            tasks.append(self.fetch_exchange_rates(date))

        results = await asyncio.gather(*tasks)
        for result in results:
            exchange_rates.append(result)

        return exchange_rates

    async def close_session(self):
        await self.session.close()

def main():
    parser = argparse.ArgumentParser(description="Fetch exchange rates for EUR and USD from PrivatBank API.")
    parser.add_argument("days", type=int, help="Number of days to retrieve exchange rates for (up to 10)")
    args = parser.parse_args()

    if args.days > 10:
        print("Error: Number of days should not exceed 10.")
        return

    start_date = datetime.now()
    fetcher = ExchangeRateFetcher()
    loop = asyncio.get_event_loop()
    exchange_rates = loop.run_until_complete(fetcher.get_exchange_rates(start_date, args.days))

    formatted_rates = []
    for rates in exchange_rates:
        date = rates["date"]
        eur_rates = next(rate for rate in rates["exchangeRate"] if rate["currency"] == "EUR")
        usd_rates = next(rate for rate in rates["exchangeRate"] if rate["currency"] == "USD")

        formatted_rates.append({
            date: {
                "EUR": {
                    "sale": eur_rates["saleRate"],
                    "purchase": eur_rates["purchaseRate"]
                },
                "USD": {
                    "sale": usd_rates["saleRate"],
                    "purchase": usd_rates["purchaseRate"]
                }
            }
        })

    print(formatted_rates)

    loop.run_until_complete(fetcher.close_session())

if __name__ == "__main__":
    main()