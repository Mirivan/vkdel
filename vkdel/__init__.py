__version__ = 1
__name__ = "VKDel"
__description__ = "Broadcast a message from VK chat to Telegram and vice versa."

from .modas import load

from logging import INFO, basicConfig, getLogger

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=INFO
)

LOGS = getLogger(__name__)

load()
