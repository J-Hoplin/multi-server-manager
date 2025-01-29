from threading import Lock
from typing import Any, Dict


class ApplicationStateManger:
    """
    Application Global State Manager

    __instance: State Manger Instance
    __lock: Thread Lock for illegal access
    """

    __instance = None
    __lock = Lock()
    __state = {}

    @classmethod
    def get_manager(cls):
        """
        Get State Manager Instance
        :return: State Manager Instance
        """
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = ApplicationStateManger()
            return cls.__instance

    def __init__(self):
        self.__state: Dict[str, Any] = {}

    @classmethod
    def set_state(cls, key: str, value: Any):
        print(cls.__state)
        cls.__state[key] = value

    @classmethod
    def get_state(cls, key: str):
        print(cls.__state)
        return cls.__state.get(key, None)

    @classmethod
    def remove_state(cls, key: str):
        if key in cls.__state:
            del cls.__state[key]
