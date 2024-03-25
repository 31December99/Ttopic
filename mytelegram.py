# -*- coding: utf-8 -*-
import asyncio
import os

from telethon import TelegramClient, errors
from decouple import config
from telethon.errors import SessionPasswordNeededError
from datetime import datetime


class MyTelegram:
    """Telegram login"""

    API_ID = config('YOUR_API_ID')
    API_HASH = config('YOUR_API_HASH')
    PHONE = config('YOUR_PHONE_NUMBER')
    SESSION = config('SESSION_NAME')
    INVITE_LINK = config('INVITE_LINK')
    WORKERS = 3  # Greater = Better internet connection

    def __init__(self):
        # Telegram Takeout instance
        self.__takeout = None
        # Channel entity
        self.__channel = None
        # Telgram client
        self.__client = None

    @property
    def takeout(self):
        return self.__takeout

    @property
    def channel(self):
        return self.__channel

    @property
    def client(self):
        return self.__client

    async def connect(self):
        """
        Connect to telegram

        retry_delay: wait for n seconds if connect fails then retry
        flood_sleep_threshold : telethon sleeps if flow_wait error < 240s occurs
        """
        self.__client = TelegramClient(session=self.SESSION,
                                       api_id=self.API_ID,
                                       api_hash=self.API_HASH,
                                       retry_delay=10,
                                       flood_sleep_threshold=240)  # 240 seconds
        await self.__client.connect()

    async def delete_file(self, filename):
        os.remove(filename)

    async def login(self):
        """
            Login to telegram after auth check
        """

        # Call connect method and config the client
        await self.connect()

        # Is this your first login ?
        if not await self.__client.is_user_authorized():
            print("Request auth...")
            await self.__client.send_code_request(self.PHONE)
            try:
                await self.__client.sign_in(phone=self.PHONE, code=int(input('Enter code: ')))
            except SessionPasswordNeededError:
                # if a password is set
                password = input("Put your password: ")
                await self.__client.sign_in(password=password)

        # Get a takeout instance
        try:
            async with self.__client.takeout(finalize=False) as conn:
                self.__channel = await conn.get_input_entity(self.INVITE_LINK)
                self.__takeout = conn
                print(f"Connected...")
        except errors.TakeoutInitDelayError:
            print("step1 > Confirm auth telegram channel  (+42777)")
            print("step2 > Restart app")
        except errors.InviteHashExpiredError as err:
            print("Wrong or invalid link!", err)

    async def worker(self, queue):
        while True:
            queue_item = await queue.get()
            msgbody, directory, title = queue_item[:3]
            current_time = datetime.now().strftime('%H:%M')
            filename = os.path.join(directory, title)
            if msgbody is not None:
                try:
                    print(f"[{current_time}] Download -> [{filename}]")
                    await self.takeout.download_media(msgbody, filename)
                except errors.FileReferenceExpiredError:
                    print(f"[{current_time}] §Expired§ => {filename} ")
                    await self.delete_file(filename)
                except errors.TimeoutError:
                    print(f"[{current_time}] §Incomplete§ => {filename} ")
                    await self.delete_file(filename)
                else:
                    print(f"[{current_time}] Completed ! {filename} ")
                finally:
                    # Chiudi e decrementa la coda di 1 con task_done()
                    queue.task_done()
            else:
                current_time = datetime.now().strftime('%H:%M')
                print(f"[{current_time}] Message not found ! {title}")
                queue.task_done()

    async def downloader(self, media_list):
        # We ask the user to enter the path to the directory
        directory = input("Введите путь к директории для сохранения файлов: ")
        # Check if the specified directory exists
        if not os.path.exists(directory):
            print("Указанная директория не существует.")
            return

        # Prepara i workers
        print("...Starting download...")
        queue = asyncio.Queue(1)
        workers = [asyncio.create_task(self.worker(queue)) for _ in range(self.WORKERS)]
        for media in media_list:
            async for messg in self.takeout.iter_messages(self.channel.channel_id, wait_time=1, ids=int(media.msgid)):
                await queue.put((messg, directory, f'{str(media.title)}_{media.msgid}'))
        await queue.join()
        # Cleaning
        for active_workers in workers:
            active_workers.cancel()
