def load():
    from .Telegram import bot
    from .VKontakte import bot as vkbot
    from .. import LOGS

    from multiprocessing import Process
    p1 = Process(target=bot.run_until_disconnected)
    p2 = Process(target=vkbot.run_forever)

    LOGS.info("Starting Telegram...")
    p1.start()
    LOGS.info("Starting VKontakte...")
    p2.start()
