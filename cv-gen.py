#!/usr/bin/env python

from typing import Any
import sys
from services import DataScv
from txparser import Parser
from log import debug_on, debug_print

# debug_on()

args = sys.argv
profile_data_path = args[1] if len(args) > 1 else "profile-data.yaml"
yaml = DataScv(profile_data_path)

yaml.load_yaml()

#load tex file
with open("input.tex", "r") as tex_file:
  tex = tex_file.read()
  debug_print("tex file loaded")

  #parse tex file
  parser = Parser()
  parser.generate(tex)
  output = parser.exec(yaml.get_data())

  #write to output file
  with open("output.tex", "w") as output_file:
    output_file.write(str(output))

    debug_print("tex file written")
    print("Done!")