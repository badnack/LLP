import sys

class Tokenizer:
  def __init__(self, input_string = ""):
    self.input_string = input_string
    self.pos = 0
    self.last_pos = 0
    self.current_token = ("", "")

  def load_string(self, input_string):
    self.input_string = input_string
    self.pos = 0
    self.last_pos = 0
    self.current_token = ("", "")

  def load_file(self, input_file):
    with open(input_file, "r") as f:
      self.input_string = f.read()
    self.pos = 0
    self.last_pos = 0
    self.current_token = ("", "")

  def at_end(self):
    # skip whitespace
    while self.pos < len(self.input_string) and self.input_string[self.pos].isspace():
      self.pos += 1
    if self.pos < len(self.input_string):
      return False
    else:
      return True

  def put_back(self):
    self.pos = self.last_pos

  def next_token(self):
    # skip whitespace
    while self.pos < len(self.input_string) and self.input_string[self.pos].isspace():
      self.pos += 1

    self.last_pos = self.pos
    if self.pos >= len(self.input_string):
      self.current_token = ("", "eof")
    elif self.input_string[self.pos: self.pos+2] == "o-":
      self.pos += 2
      self.current_token = ("o-", "lollipop")
    elif self.input_string[self.pos].isalpha() or self.input_string[self.pos] == "_":
      while self.input_string[self.pos].isalnum() or self.input_string[self.pos] == "_":
        self.pos += 1
      self.current_token = (self.input_string[self.last_pos:self.pos], "string")
    elif self.input_string[self.pos] in "()":
      self.current_token = (self.input_string[self.pos], "parenthesis")
      self.pos += 1
    elif self.input_string[self.pos] == "=":
      self.current_token = ("=", "unify")
      self.pos += 1
    elif self.input_string[self.pos] in ".,":
      self.current_token = (self.input_string[self.pos], "punctuation")
      self.pos += 1
    elif self.input_string[self.pos] == "!":
      self.current_token = (self.input_string[self.pos], "ofcourse")
      self.pos += 1
    elif self.input_string[self.pos] == "@":
      self.current_token = (self.input_string[self.pos], "affine")
      self.pos += 1
    else:
      print "Invalid token:", self.input_string[self.pos: self.pos+5]
      sys.exit(0)
    return self.current_token



