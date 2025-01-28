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

    def __new__(cls, *args, **kwargs):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__new__(cls)
            return cls.__instance

    def __init__(self):
        self.__state: Dict[str, Any] = {}

    def set_state(self, key: str, value: Any):
        self.__state[key] = value

    def get_state(self, key: str):
        return self.__state.get(key, None)
