
class MyMedia:

    def __init__(self):
        self.__title = None
        self.__id = None

    @property
    def title(self):
        return self.__title

    @property
    def msgid(self):
        return self.__id

    @title.setter
    def title(self, value):
        self.__title = value

    @msgid.setter
    def msgid(self, value):
        self.__id = value

    def saved(self) -> bool:
        return True if (self.__title and
                        self.__id) else False

    def __str__(self):
        print(self.__title, self.__id)
