import json
from typing import Any
import magic
import yaml
from helpers.log import getLogger

logger = getLogger(__name__)

class ProfileData:
  def __init__(self, path: str):
    self.path = path
    self.data: dict[str, Any] = {}

  def load_data(self):
    with open(self.path, "r") as stream:
      try:
        logger.debug('Reading File: ' + self.path + '...')
        if self.path.endswith('.yaml') or self.path.endswith('.yml'):
          self.data.update(yaml.safe_load(stream))
        elif self.path.endswith('.json'):
          self.data.update(json.load(stream))
        else:
          logger.error('Unsupported file type!')
          exit(-1)
      except yaml.YAMLError as exc:
        print(exc)
        exit(-1)

  def get_data(self, *keys: str):
    data = self.data
    if len(keys) > 0:
      for key in keys:
        data = data[key]

    return data
