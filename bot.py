import config
import handlers
from vkbottle.bot import Bot, Message
from loguru import logger
from client import client


__version__ = '0.0.7'
__all__ = ['client', '__version__']

def main():
    print(f"Tavrbot version {__version__} started!")
    client.run_forever()

if __name__ == '__main__':
    main()
