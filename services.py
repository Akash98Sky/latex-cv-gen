from typing import Any
import yaml
from log import getLogger

logger = getLogger(__name__)

class DataScv:
  def __init__(self, path: str):
    self.path = path
    self.yaml_data: dict[str, Any] = {}

  def load_yaml(self):
    with open(self.path, "r") as stream:
      try:
        logger.debug('Reading File: ' + self.path + '...')
        self.yaml_data.update(yaml.safe_load(stream))
      except yaml.YAMLError as exc:
        print(exc)
        exit(-1)

  def get_data(self, *keys: str):
    data = self.yaml_data
    if len(keys) > 0:
      for key in keys:
        data = data[key]

    return data
