from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging


storage = MemoryStorage()
dp = Dispatcher()
pool = None


class ColoredFormatter(logging.Formatter):
    COLORS = {'DEBUG': '\033[94m', 'INFO': '\033[92m', 'WARNING': '\033[93m',
              'ERROR': '\033[91m', 'CRITICAL': '\033[95m'}

    def format(self, record):
        log_fmt = f"{self.COLORS.get(record.levelname, '')}%(message)s\033[0m"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)
