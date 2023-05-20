from typing import Any
from txtree import OperationTree, TreeNode, DataNode, EvalDataNode, ForLoopNode, JoinOperatorNode
import re
  
class TreeBuilder():
  varTokenRegex = r"\${([\w.]+)}"
  forTokenRegex = r"\${for\(([\w]+:[\w.]+)\)\(([\w\W]*)\)}"

  def buildForLoopNode(self, forExp: str, forBody: str):
    childern: list[TreeNode] = []
    matches = re.finditer(self.forTokenRegex, forBody, re.MULTILINE)
    nonMatchStart = 0

    for match in matches:
      childern.append(self.buildDataNode(forBody[nonMatchStart:match.start()]))
      # get for loop body and pass it to ForLoopNode
      nestedForExp = match.groups()[0]
      nestedForBody = match.groups()[1]
      childern.append(self.buildForLoopNode(nestedForExp, nestedForBody))
      nonMatchStart = match.end()
    childern.append(self.buildDataNode(forBody[nonMatchStart:]))

    evalTokenRegex = r"\${([A-Za-z0-9.]+)}"
    itemVar = forExp.split(':')[0]
    listVar = forExp.split(':')[1]

    return ForLoopNode(itemVar, listVar, childern)
  
  def buildDataNode(self, data: str):
    matches = re.finditer(self.varTokenRegex, data, re.MULTILINE)
    nonMatchStart = 0
    childern: list[TreeNode] = []
    for match in matches:
      childern.append(DataNode(data[nonMatchStart:match.start()]))
      childern.append(EvalDataNode(match.groups()[0]))
      nonMatchStart = match.end()
    childern.append(DataNode(data[nonMatchStart:]))

    return JoinOperatorNode(childern)

  def build(self, data: str):
    forLoopMatches = re.finditer(self.forTokenRegex, data, re.MULTILINE)
    nonMatchStart = 0
    childern: list[TreeNode] = []
    for match in forLoopMatches:
      childern.append(self.buildDataNode(data[nonMatchStart:match.start()]))
      # get for loop body and pass it to ForLoopNode
      forExp = match.groups()[0]
      forBody = match.groups()[1]
      childern.append(self.buildForLoopNode(forExp, forBody))
      nonMatchStart = match.end()
    childern.append(self.buildDataNode(data[nonMatchStart:]))

    return JoinOperatorNode(childern)

class Parser:
  def __init__(self):
    self.tree = OperationTree()
    pass

  def generate(self, data: str):
    builder = TreeBuilder()
    self.tree.set(builder.build(data))

  def exec(self, dict: dict):
    return self.tree.execute(dict)
    
