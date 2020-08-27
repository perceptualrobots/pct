# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_utilities.ipynb (unless otherwise specified).

__all__ = ['UniqueNamer', 'FunctionsList']

# Cell
class UniqueNamer:
    __instance = None
    @staticmethod
    def getInstance():
      """ Static access method. """
      if UniqueNamer.__instance == None:
         UniqueNamer()
      return UniqueNamer.__instance

    def __init__(self):
      """ Virtually private constructor. """
      if UniqueNamer.__instance != None:
         raise Exception("This class is a singleton!")
      else:
         UniqueNamer.__instance = self
      self.names = {}

    def clear(self):
      self.names = {}

    def get_name(self, name):
        if name in self.names.keys():
            num = self.names[name]+1
            self.names[name]=num
            name = f'{name}{num}'
        else:
            self.names[name]=0
        return name

# Cell
class FunctionsList:
    __instance = None
    @staticmethod
    def getInstance():
      """ Static access method. """
      if FunctionsList.__instance == None:
         FunctionsList()
      return FunctionsList.__instance
    def __init__(self):
      """ Virtually private constructor. """
      if FunctionsList.__instance != None:
         raise Exception("This class is a singleton!")
      else:
         FunctionsList.__instance = self
      self.functions = {}

    def clear(self):
      self.functions = {}


    def add_function(self, func):
        name = func.get_name()
        self.functions[name]=func

        return name

    def get_function(self, name):
        func = self.functions[name]

        return func