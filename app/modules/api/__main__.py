from app.config.config import load_env
from app.utils.logger import setup_logger

load_env()
logger = setup_logger(__name__)

from app.modules.api.app import run

if __name__ == "__main__":
    run()
