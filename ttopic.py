import asyncio
from group import Group


async def main():
    # New Group istance
    group = Group()

    # Connect to group
    await group.connect()

    # Get topic ID and Image list
    media_list = await group.topic(await group.input())

    # Downloader..
    input(f"\nPress enter to start the download ")
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
