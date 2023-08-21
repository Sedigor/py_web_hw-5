import argparse
import aiohttp
import asyncio
import json
from datetime import datetime, timedelta

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="

async def fetch_exchange_rates(session, date):
    async with session.get(API_URL + date) as response:
        return await response.json()

async def get_exchange_rates(start_date, days):
    async with aiohttp.ClientSession() as session:
        tasks = []
        exchange_rates = []

        for day in range(days):
            date = (start_date - timedelta(days=day)).strftime("%d.%m.%Y")
            tasks.append(fetch_exchange_rates(session, date))

        results = await asyncio.gather(*tasks)
        for result in results:
            exchange_rates.append(result)

        return exchange_rates

def main():
    parser = argparse.ArgumentParser(description="Fetch exchange rates for EUR and USD from PrivatBank API.")
    parser.add_argument("days", type=int, help="Number of days to retrieve exchange rates for (up to 10)")
    args = parser.parse_args()

    if args.days > 10:
        print("Error: Number of days should not exceed 10.")
        return

    start_date = datetime.now()
    exchange_rates = asyncio.run(get_exchange_rates(start_date, args.days))

    formatted_rates = []
    for rates in exchange_rates:
        date = rates["date"]
        eur_rates = rates["exchangeRate"][0]
        usd_rates = rates["exchangeRate"][1]

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

    print(json.dumps(formatted_rates, indent=2))

if __name__ == "__main__":
    main()
