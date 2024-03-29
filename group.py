# -*- coding: utf-8 -*-

from mytelegram import MyTelegram
from mymedia import MyMedia
from telethon import functions, errors
from datetime import datetime

class Album:

    def __init__(self, topic_id: int, grouped_id: int):
        self.grouped_id = grouped_id
        self.topic_id = topic_id


class Group:

    def __init__(self):
        self.telegram = MyTelegram()
        self.media_raw = []
        self.media = None

    async def connect(self):
        await self.telegram.login()
        print(f"-> [INVITE LINK] {self.telegram.INVITE_LINK}")
        print(f"-> [CHANNEL ID]  {self.telegram.channel.channel_id}")

    async def topic(self, topic_id: int, topic_title: str):
        """
         Select a topic and add each photo to the media_list
        :return:
        """
        async for message in self.telegram.client.iter_messages(self.telegram.channel.channel_id,
                                                                limit=None,
                                                                reverse=True,
                                                                wait_time=1,
                                                                reply_to=topic_id,
                                                                min_id=0,
                                                                max_id=0):
            if not message.sticker and not hasattr(message.media, 'document'):
                if message.grouped_id or message.photo:
                    self.media = MyMedia()
                    self.media.msgid = message.id
                    self.media_raw.append(self.media)
                    # Converting a timestamp to a datetime object
                    message_time = datetime.fromtimestamp(message.date.timestamp())
                    # Formatting the time into a string with the usual format
                    formatted_time = message_time.strftime("%Y-%m-%d %H-%M-%S")
                    # Setting the file name using the usual time format
                    self.media.title = f"{formatted_time}_{message.id}.jpg"
                    print(self.media.title)

        print(f"Found n° {len(self.media_raw)} Photo")

        return [media for media in self.media_raw if media.msgid]

    async def forum_topics(self) -> list:
        """
         Using TL reference : https://docs.telethon.dev/en/stable/concepts/full-api.html#functions
        Get a list of topics from a channel entity
        :param topic_id: topic ID
        :return: list of topics
        """
        try:
            result = await self.telegram.client(functions.channels.GetForumTopicsRequest(
                channel=self.telegram.channel,  # channel entity
                offset_date=None,
                offset_id=0,
                offset_topic=0,
                limit=50,  # Hardcoded see pagination - https://core.telegram.org/api/offsets
                q=None
            ))

        except errors.ChannelForumMissingError:
            print("No topics found.")
            return []

        print(".:LIST OF TOPICS:.")
        topic_ids = [[topic.id, topic.title] for topic in result.topics]
        for index, (topic_id, topic_title) in enumerate(sorted(topic_ids)):
            print(f"[{index}] {topic_title} {topic_id}")
        return sorted(topic_ids)
