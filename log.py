DEBUG = False

def debug_on():
  global DEBUG
  DEBUG = True

def debug_off():
  global DEBUG
  DEBUG = False

def debug_print(*args):
  if DEBUG:
    print(*args)