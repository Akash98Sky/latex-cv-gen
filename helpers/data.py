import json
from typing import Any
import yaml
from helpers.log import getLogger

logger = getLogger(__name__)
escape_chars = ['\\', '$', '%', '#', '{', '}', '&']

def __escape(data: str):
  for char in escape_chars:
    data = data.replace(char, '\\' + char)
  return data

def sanitize_data(data: dict[str, Any] | list):
  if isinstance(data, dict):
    for key in data:
      val = data[key]
      if isinstance(val, str):
        data[key] = __escape(val)
      elif isinstance(val, list) or isinstance(val, dict):
        sanitize_data(val)
  else:
    for i in range(len(data)):
      val = data[i]
      if isinstance(val, str):
        data[i] = __escape(val)
      elif isinstance(val, list) or isinstance(val, dict):
        sanitize_data(val)

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
        sanitize_data(self.data)
      except yaml.YAMLError as exc:
        print(exc)
        exit(-1)

  def get_data(self, *keys: str):
    data = self.data
    if len(keys) > 0:
      for key in keys:
        data = data[key]

    return data
