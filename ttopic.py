import asyncio
from group import Group


async def main():
    # New Group istance
    group = Group()

    # Connect to group
    await group.connect()

    # Get your Topics list
    list_of_topics = await group.forum_topics()
    while True:
        index = input(f"Choose which topic you want to download (0-{len(list_of_topics) - 1}): ")
        if index.isnumeric():
            topic_index = int(index)
            if 0 <= topic_index <= len(list_of_topics) - 1:
                break

    topic_id, topic_title = list_of_topics[topic_index]
    media_list = await group.topic(topic_id, topic_title)
    input(f"\n[DOWNLOAD TOPIC PHOTO '{topic_title}'] - Press enter to continue")
    await group.telegram.downloader(media_list)

    loop.stop()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        task_main = loop.create_task(main())
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        pass
