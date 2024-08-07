import logging

root_logger = logging.getLogger('latex-cv-gen')
logging.basicConfig(level = logging.INFO)

def debug_on():
  logging.basicConfig(level = logging.DEBUG)
  root_logger.setLevel(logging.DEBUG)

def debug_off():
  logging.basicConfig(level = logging.INFO)
  root_logger.setLevel(logging.INFO)

def getLogger(name: str | None = None):
  return root_logger.getChild(name) if name else root_logger