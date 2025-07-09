import asyncio

from app.modules.worker.app import run

if __name__ == "__main__":
    asyncio.run(run())