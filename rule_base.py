import tokenizer
import sys
from itertools import count

class Variable:
  def __init__(self):
    self.name = ""
    self.subvars = list()
    self.parent = None
    self.var_type = None

  def pp(self, follow_parent=False):
    ppstr = ""
    if self.var_type is None:
      pass
# can uncomment for testing, but will output ! and @ to the user
#    else:
#      ppstr += self.var_type

    to_follow = self
    if follow_parent:
      while to_follow.parent is not None:
        to_follow = to_follow.parent
    ppstr += to_follow.name
    if len(to_follow.subvars) > 0:
      ppstr += "("
      for i, var in enumerate(to_follow.subvars):
        ppstr += var.pp(follow_parent)
        if i < len(to_follow.subvars) - 1:
          ppstr += ", "
      ppstr += ")"
    return ppstr

  def is_temp(self):
    return self.name[0].isupper()

class TempVar:
  _ids = count(0)
  def __init__(self):
    self.id = self._ids.next()
    self.name = "_temp" + str(self.id)
    self.subvars = list()
    self.parent = None
    self.var_type = None

  def pp(self, follow_parent=False):
    to_follow = self
    if follow_parent:
      while to_follow.parent is not None:
        to_follow = to_follow.parent
    ppstr = to_follow.name
    if len(to_follow.subvars) > 0:
      ppstr += "("
      for i, var in enumerate(to_follow.subvars):
        ppstr += var.pp(follow_parent)
        if i < len(to_follow.subvars) - 1:
          ppstr += ", "
      ppstr += ")"
    return ppstr

  def is_temp(self):
    return True

# left side should be a Variable
# right side should be a set of Variables
# if right side is empty then it is a fact, ie right side is true.
class Rule:
  def __init__(self):
    self.left_side = None
    self.right_side = list()

  def pp(self, follow_parent=False):
    ppstr = "("
    ppstr += self.left_side.pp(follow_parent)
    ppstr += "o- "
    for var in self.right_side:
      ppstr += var.pp(follow_parent)
      ppstr += ", "
    ppstr += ")"
    return ppstr

class RuleBase:
  def __init__(self):
    self.tokenizer = None

  def load_goal_from_string(self, goal_str):
    self.tokenizer = tokenizer.Tokenizer()
    self.tokenizer.load_string(goal_str)
    goals = list()
    
    while 1:
      goal = self.read_variable()
      goals.append(goal)
      token = self.tokenizer.next_token()
      if token[0] == '.':
        break
      elif token[0] != ',':
        print "error expected , between query goals"
        sys.exit(0)

    self.tokenizer.put_back()
    # check that the next tokens are . and eof
    token = self.tokenizer.next_token()
    token2 = self.tokenizer.next_token()
    if token[0] != "." or token2[1] != "eof":
      print "expected . at end of rule, but read:", token[0], token2[0]
      sys.exit(0)
    return goals

  def get_var_names_from_string(self, input_str):
    self.tokenizer = tokenizer.Tokenizer()
    self.tokenizer.load_string(input_str)
    var_names = []

    token = self.tokenizer.next_token()
    while token[1] != "eof":
      if token[1] == "string" and token[0].isupper() and token[0] not in var_names:
        var_names.append(token[0])
      token = self.tokenizer.next_token()

    return var_names

  def load_rules_from_file(self, filename):
    # init tokenizer
    self.tokenizer = tokenizer.Tokenizer()
    self.tokenizer.load_file(filename)
    rules = list()
    # read all rules
    while not self.tokenizer.at_end():
      new_rule = self.read_rule()
      token = self.tokenizer.next_token()
      if token[0] != ".":
        print "Parsing error expected . at:", token[0], \
              self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
        sys.exit(0)

      # TODO: check rule, make sure it is valid
      #print  "Rule", len(rules), ":", new_rule.pp()
      rules.append(new_rule)
    return rules

  def read_rule(self):
    rule = Rule()
    left_variables = list()
    while 1:
      var = self.read_variable()
      left_variables.append(var)
      token = self.tokenizer.next_token()
      if token[0] == "o-" or token[0] == '.':
        self.tokenizer.put_back()
        break
      elif token[0] != ',':
        print "error expected , between left side variables"
        sys.exit(0)
    

    left_var = Variable()
    left_var.name = "and__"
    left_var.subvars = left_variables
    rule.left_side = left_var
    
    token = self.tokenizer.next_token()
    if token[0] == "o-":
      # read right side
      rule.right_side = self.read_right_side()
    else:
      self.tokenizer.put_back()
    # if no right side just leave right side as the empty set (which implies true)
    return rule

  def read_right_side(self):
    # handle parentheses
    token = self.tokenizer.next_token()
    if token[0] == "(":
      result = self.read_right_side()
      token = self.tokenizer.next_token()
      if token[0] != ")":
        print "Parsing error expected ) at:", token[0], \
              self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
        sys.exit(0)
      return result
    else:
      self.tokenizer.put_back()

    # read right side vars
    temp_right_side = list()
    token = self.tokenizer.next_token()
    while token[0] != "." and token[0] != ")" and token[1] != "eof":
      if token[0] == "(":
        temp_right_side += self.read_right_side()
        token = self.tokenizer.next_token()
        if token[0] != ")":
          print "Parsing error expected ) at:", token[0], \
                self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
          sys.exit(0)
      elif token[1] == "string" or token[0] == '!' or token[0] == '@':
        self.tokenizer.put_back()
        temp_right_side.append(self.read_variable())
      elif token[0] != "," and token[0] != "." and token[0] != ")":
        print "Parsing error expected . at, or unexpected token:", token[0], \
              self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
        sys.exit(0)
      token = self.tokenizer.next_token()

    # check that there actually was something read
    if len(temp_right_side) == 0:
      print "Parsing error expected statement at:", token[0], \
            self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
      sys.exit(0) 

    self.tokenizer.put_back()
    return temp_right_side

  # probably need to separate out hypothetical, hypothetical allowed some cases, not all
  def read_variable(self):

    token = self.tokenizer.next_token()
    var_type = None
    if token[0] == '!' or token[0] == '@':
      var_type = token[0]
    else:
      self.tokenizer.put_back()

    token = self.tokenizer.next_token()
    if token[0] == "(":
      result = self.read_variable()
      token = self.tokenizer.next_token()
      if token[0] != ")":
        print "Parsing error expected ) at:", token[0], \
              self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
        sys.exit(0)
      if result.var_type is None:
        result.var_type = var_type
      return result

    elif token[1] != "string":
      print "Parsing error expected string at:", token[0], \
            self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
      sys.exit(0)
    # var name
    var = Variable()
    var.name = token[0]
    token = self.tokenizer.next_token()
    # check if variable is a function
    if token[0] == "(":
      # check that variable name is lower case
      if var.name[0].isupper():
        print "Syntax error function name should be lower case:", var.name, token[0], \
              self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
        sys.exit(0)
      # read sub variables
      var.subvars.append(self.read_variable())
      token = self.tokenizer.next_token()
      while(token[0] == ","):
        var.subvars.append(self.read_variable())
        token = self.tokenizer.next_token()
      if token[0] != ")":
        print "Parsing error expected ) at:", token[0], \
              self.tokenizer.next_token()[0], self.tokenizer.next_token()[0]
        sys.exit(0)
    else:
      # not a function so put back the next token
      self.tokenizer.put_back()
    var.var_type = var_type
    return var

  @staticmethod
  def make_and(variables):
    var = Variable()
    var.name = "and__"
    var.subvars = variables
    return var





