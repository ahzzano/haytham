from __future__ import annotations

import yaml
from yaml import YAMLObject

class Config:
    configuration: dict 

    def __init__(self, conf: dict):
        self.configuration = conf
        pass

    @classmethod
    def load_config(cls, fn: str) -> Config:
        with open(fn, 'r') as file:
            conf = dict(yaml.safe_load(file))
            
        config_object = cls(conf)

        return config_object
    
    def get_token(self) -> str:
        return self.configuration['token']
            

            

