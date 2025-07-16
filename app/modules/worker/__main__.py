from app.config.config import load_env
from app.utils.logger import setup_logger

load_env()
logger = setup_logger(__name__)

import asyncio

from app.modules.worker.app import run

if __name__ == "__main__":
    asyncio.run(run())