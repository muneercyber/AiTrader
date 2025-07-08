import asyncio
from telegram_bot import start_telegram_bot
from trade_logic import continuous_analysis_loop

async def main():
    await asyncio.gather(
        start_telegram_bot(),
        continuous_analysis_loop()
    )

if __name__ == "__main__":
    asyncio.run(main())
