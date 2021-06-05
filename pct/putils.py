# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_putils.ipynb (unless otherwise specified).

__all__ = ['UniqueNamer', 'FunctionsList', 'get_drive', 'get_gdrive', 'Counter', 'stringIntListToListOfInts',
           'stringFloatListToListOfFloats', 'stringListToListOfStrings', 'listNumsToString', 'sigmoid', 'smooth',
           'show_video', 'wrap_env', 'is_in_notebooks']

# Cell


# Cell
class UniqueNamer:
    "A utility for ensuring the names of functions are unique."
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
        #else:
        self.names[name]=0
        return name

# Cell
class FunctionsList:
    "A utility for storing functions created, keyed on the function name."
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

    def remove_function(self, name):
        self.functions.pop(name)

    def get_function(self, name):
        if isinstance(name, str) and name in self.functions:
            func = self.functions[name]
        else:
            func = name
        return func

    def report(self, name=None):
        if name == None:
            print(len(self.functions))
            for key in self.functions.keys():
                print("*** ", key, [self.functions[key]])
                print(self.functions[key])
        else:
            print("*** ", key, [self.functions[key]])
            print(self.functions[key])


# Cell
def get_drive():
    if os.name == 'nt':
        drive = os.path.abspath(os.sep)
    else:
        drive = os.path.abspath(os.sep)+'mnt'+os.sep+'c'+os.sep
    return drive

# Cell
def get_gdrive():
    if socket.gethostname() == 'DESKTOP-5O07H5P':
        root_dir='/mnt/c/Users/ruper/Google Drive/'
        if os.name == 'nt' :
            root_dir='C:\\Users\\ruper\\Google Drive\\'
    else:
        root_dir='/mnt/c/Users/ryoung/Google Drive/'
        if os.name == 'nt' :
            root_dir='C:\\Users\\ryoung\\Google Drive\\'
    return root_dir

# Cell
class Counter(object):

  def __init__(self, limit=1000, init=0, step=1, print=100, pause=False, display=10):
      self.limit=limit
      self.counter=init
      self.step=step
      self.print=print
      self.pause=pause
      self.display=display


  def __call__(self):
      self.counter+=self.step
      return self.counter

  def get(self):
      return self.counter

  def get_limit(self):
      return self.limit

  def set_limit(self, limit):
      self.limit=limit


# Cell
def stringIntListToListOfInts(strList, delimiter):
    #listRes = list(strList.split(","))
    #print(listRes)
    result = []
    for item in strList.strip('][').split(','):
        result.append(int(item))
    return result

# Cell
def stringFloatListToListOfFloats(strList, delimiter):
    #listRes = list(strList.split(","))
    #print(listRes)
    result = []
    for item in strList.strip('][').split(','):
        result.append(float(item))
    return result

# Cell
def stringListToListOfStrings(strList, delimiter):
    #listRes = list(strList.split(","))
    #print(listRes)
    result = []
    for item in strList.strip('][').split(','):
        result.append(item.strip())
    return result

# Cell
def listNumsToString(list):
    str = ""
    for item in list:
        str += f'{item}'
    return str

# Cell
def sigmoid(x, range, scale) :
    return -range / 2 + range / (1 + np.exp(-x * scale / range));

# Cell
def smooth(new_val, old_val, smooth_factor):
    return old_val * smooth_factor + new_val * (1-smooth_factor)

# Cell
def show_video():
  mp4list = glob.glob('video/*.mp4')
  if len(mp4list) > 0:
    mp4 = mp4list[0]
    video = io.open(mp4, 'r+b').read()
    encoded = base64.b64encode(video)
    ipythondisplay.display(HTML(data='''<video alt="test" autoplay
                 controls style="height: 400px;">
                <source src="data:video/mp4;base64,{0}" type="video/mp4" />
             </video>'''.format(encoded.decode('ascii'))))
  else:
    print("Could not find video")

def wrap_env(env):
  env = Monitor(env, './video', force=True)
  return env

# Cell
import os
from pathlib import Path

def is_in_notebooks():
    term = os.getenv('TERM')
    if term == 'xterm-color':
        return True

    return False