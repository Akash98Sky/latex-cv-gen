from typing import Any
from log import debug_print


class TreeNode:
  def __init__(self, data):
    self.data = data
    self.children = []

  def add_child(self, obj):
    self.children.append(obj)

  def __str__(self):
    return self.data
  

class DataNode(TreeNode):
  data: Any
  props: dict[str, Any]

  def __init__(self, data: Any, props: dict[str, Any] = {}):
    super().__init__(data)
    self.props = props

  def __str__(self):
    return str(self.data)
  
  def evaluate(self, dict: dict[str, Any]):
    return self.data
  
class EvalDataNode(DataNode):
  def __init__(self, exp: str):
    super().__init__(exp)

  def __str__(self):
    return f'${{{self.data}}}'
  
  def evaluate(self, dict: dict[str, Any]):
    val = dict
    for key in self.data.split('.'):
      val = val[key]
    if (isinstance(val, str)):
      escSeqLst = ['$', "#" , '{', '}', '&']
      for escSeq in escSeqLst:
        val = val.replace(escSeq, f'\\{escSeq}')
    return DataNode(val)
  
class ForLoopNode(DataNode):
  def __init__(self, itemVar: str, listVar: str, body: list[TreeNode]):
    super().__init__('for', {'listVar': listVar, 'itemVar': itemVar})
    for child in body:
      self.add_child(child)

  def __str__(self):
    return f'${{for({self.props["itemVar"]}:{self.props["listVar"]})({"".join([str(child) for child in self.children])})}}'
  
  def evaluate(self, dict: dict[str, Any]):
    itemVar = self.props['itemVar']
    listVar = self.props['listVar']
    list = EvalDataNode(listVar).evaluate(dict).data
    result = []
    for item in list:
      result.append(''.join([str(child.evaluate({**dict, itemVar: item})) for child in self.children]))

    return DataNode('\n'.join(result))
  
class JoinOperatorNode(DataNode):
  def __init__(self, nodes: list[TreeNode]):
    super().__init__('+')
    for node in nodes:
      self.add_child(node)

  def __str__(self):
    return '+'.join([str(child) for child in self.children])
  
  def evaluate(self, dict: dict[str, Any]):
    evalChildren: list[DataNode] = []
    for child in self.children:
      evalChildren.append(child.evaluate(dict))
    
    return DataNode(''.join([str(child) for child in evalChildren]))


class OperationTree():
  root: DataNode
  def __init__(self):
    super().__init__()

  def set(self, root: DataNode):
    self.root = root
    debug_print(self.root)

  def execute(self, dict: dict[str, Any], node = None):
    if (node == None):
      node = self.root

    return node.evaluate(dict)
