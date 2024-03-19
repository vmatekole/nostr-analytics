import os
from typing import Union


class Configuration:
    def __init__(self, **kwargs: dict[str, Union[str, int]]):
        self._readonly = False

        for k, v in kwargs.items():
            setattr(self, k, v)
        self._readonly = True

    def __setattr__(self, __name: str, __v) -> None:
        if getattr(self, '_readonly', False):
            raise AttributeError('LLM configuration readonly')
        super().__setattr__(__name, __v)

    def __repr__(self) -> str:
        state = ''
        for k, v in self.__dict__.items():
            if k != '_readonly':
                state += f'{k}: {v} '
        return state

    @staticmethod
    def get_config_of_env_vars() -> 'Configuration':
        env_args = {k: v for k, v in os.environ.items()}
        config: Configuration = Configuration(**env_args)
        return config
