# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_putils.ipynb.

# %% auto 0
__all__ = ['SingletonObjects', 'UniqueNamer', 'FunctionsList', 'Memory', 'NumberStats', 'dynamic_module_import',
           'dynamic_class_load', 'get_drive', 'loadjson', 'Counter', 'stringIntListToListOfInts',
           'stringFloatListToListOfFloats', 'stringListToListOfStrings', 'listNumsToString', 'round_lists',
           'floatListsToString', 'limit_large_float', 'sigmoid', 'smooth', 'sigmoid_array', 'dot', 'list_of_ones',
           'limit_to_range', 'show_video', 'wrap_env', 'is_in_notebooks', 'printtime', 'clip_value',
           'map_to_int_odd_range', 'map_to_int_even_range', 'TimerError', 'Timer']

# %% ../nbs/01_putils.ipynb 3
import numpy as np
import sys, importlib, json, math, os, time, math
from datetime import datetime
# import warnings
# warnings.filterwarnings("error")

# %% ../nbs/01_putils.ipynb 4
class SingletonObjects:
    "A utility for refrencing objects that should only be declared once."
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if SingletonObjects.__instance == None:
           SingletonObjects()
        return SingletonObjects.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if SingletonObjects.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            SingletonObjects.__instance = self
        self.objects = {}

    def clear(self):
        self.objects = {}
            
    def get_object(self, name=None):
        return self.objects[name]

    def add_object(self, key=None, value=None):
        if key in self.objects:
            raise Exception(f'Object {key} already exists in SingletonObjects.')            
        else:
            self.objects[key]=value


# %% ../nbs/01_putils.ipynb 5
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

    def clear(self, namespace=None):
        if namespace==None:
            self.names = {}
        else:
            self.names[namespace] = {}

            
    def get_name(self, namespace=None, name=None):
        # checks if name is unqiue, if a name is not unique a new one is created, name recored 
        if namespace in self.names:
            namespace_list = self.names[namespace]
        else:
            namespace_list = {}
            self.names[namespace] = namespace_list

        if name in namespace_list: 
            num = namespace_list[name]+1
            namespace_list[name]=num
            name = f'{name}{num}'
        #else:
        namespace_list[name]=0
        return name
    
    def report(self,  namespace=None, name=None,):

        if namespace is None:
            for namespace, namespace_list in self.names.items():
                print(namespace, len(namespace_list))
                for name in namespace_list:
                    print("*** ", name)
        else:
            if namespace in self.names:
                namespace_list = self.names[namespace]
                if name == None:
                    print(len(namespace_list))
                    for nname in namespace_list:
                        print("*** ", nname, namespace_list[nname])
                else:
                    print("*** ", name, namespace_list[name])

# %% ../nbs/01_putils.ipynb 6
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

    def clear(self, namespace=None):
        if namespace==None:
            self.functions = {}
        else:
            self.functions[namespace] = {}
    
    def add_function(self, namespace=None, func=None):
        # adds a function to a namespace list, by name
        if namespace in self.functions:
            namespace_list = self.functions[namespace]
        else:
            namespace_list = {}
            self.functions[namespace]=namespace_list

        name = func.get_name()
        if name in namespace_list:
            raise Exception(f'Function {name} is already in namespace list {namespace}')
        namespace_list[name]=func
        
        return name

    def remove_function(self, namespace=None, name=None):
        if name in self.functions[namespace]:
            func = self.functions[namespace].pop(name)     
            
        if self.count(namespace)==0:
            self.functions.pop(namespace)
            
        return func
    
    def delete_function(self, namespace=None, name=None):
        func = self.remove_function(namespace=namespace, name=name)
        del func

    def get_function(self, namespace=None, name=None):     
        if  name is None:
            raise Exception(f'The function name must be specified')
        if  namespace is None:
            raise Exception(f'The namespace must be specified')
        
        if namespace in self.functions:
            namespace_list = self.functions[namespace]
        else:
            return name
        
        if isinstance(name, str) :
            if  name in namespace_list:
                func = namespace_list[name]
            else:
                raise Exception(f'Function {name} does not exist in namespace {namespace}')
        else:
            func = name

        return func
    
    def count(self, namespace=None):
        if namespace is None:
            return len(self.functions)
        
        if namespace in self.functions:
            namespace_list = self.functions[namespace]
            return len(namespace_list)
        else:
            raise Exception(f"Namespace {namespace} not found in report")
                
                
                
    def report(self, namespace=None, name=None):
        print("--- functions report")
        if namespace is None:
            for namespace, namespace_list in self.functions.items():
                print(len(namespace_list), 'NAMESPACE', namespace)
                ctr = 1
                for name, function in namespace_list.items():
                    print("*** ", ctr, name, [function])
                    print(function)
                    ctr = ctr + 1
                print()
        else:   
            if namespace in self.functions:
                namespace_list = self.functions[namespace]
            else:
                raise Exception(f"Namespace {namespace} not found in report")

            if name == None:
                print(len(namespace_list), 'NAMESPACE', namespace)
                ctr = 1
                for name, function in namespace_list.items():
                    print("*** ", ctr, name, [function])
                    print(function)
                print()
            else:
                print("*** ", name, [namespace_list[name]])
                print(namespace_list[name])          
            

# %% ../nbs/01_putils.ipynb 7
class Memory:
    "A utility for recording global values."
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if Memory.__instance == None:
           Memory()
        return Memory.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Memory.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Memory.__instance = self
        self.memory = {}

    def clear(self):
        self.memory = {}

            
    def get_data(self, key=None):
        value = None
        if key in self.memory:
            value = self.memory[key]
        return value
    
    def add_data(self, key=None, value=None):
        self.memory[key]=value



# %% ../nbs/01_putils.ipynb 8
class NumberStats:
    "A utility for calculating the statistice of a number."
    __instance = None
    @staticmethod 
    def getInstance():
        """ Static access method. """
        if NumberStats.__instance == None:
             NumberStats()
        return NumberStats.__instance
    def __init__(self):
        """ Virtually private constructor. """
        if NumberStats.__instance != None:
             raise Exception("This class is a singleton!")
        else:
             NumberStats.__instance = self
        self.max = -math.inf
        self.min = math.inf

    
    def add(self, number=None):
        if number > self.max:
            self.max = number

        if number < self.min:
            self.min = number
                
    def report(self):
        print("--- stats report")
        print(f'Max: {self.max:4.3f}')
        print(f'Min: {self.min:4.3f}')
            

# %% ../nbs/01_putils.ipynb 14
def dynamic_module_import(modulename, package=None):
    if modulename not in sys.modules:
        importlib.import_module(modulename, package)     

# %% ../nbs/01_putils.ipynb 15
def dynamic_class_load(modulename, classname):
    module = importlib.import_module(modulename) 
    my_class = getattr(module, classname)

# %% ../nbs/01_putils.ipynb 17
def get_drive():
    if os.name == 'nt':
        drive = os.path.abspath(os.sep)
    else:
        drive = os.path.abspath(os.sep)+'mnt'+os.sep+'c'+os.sep    
    return drive

# %% ../nbs/01_putils.ipynb 18
def loadjson(file):      
    with open(file) as f:
        rtn = json.load(f)
    return rtn

# %% ../nbs/01_putils.ipynb 20
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

# %% ../nbs/01_putils.ipynb 21
def stringIntListToListOfInts(strList, delimiter):
    #listRes = list(strList.split(","))
    #print(listRes)
    result = []
    for item in strList.strip('][').split(','):
        result.append(int(item))
    return result

# %% ../nbs/01_putils.ipynb 22
def stringFloatListToListOfFloats(strList, delimiter):
    #listRes = list(strList.split(","))
    #print(listRes)
    result = []
    for item in strList.strip('][').split(','):
        result.append(float(item))
    return result

# %% ../nbs/01_putils.ipynb 23
def stringListToListOfStrings(strList, delimiter=','):
    #listRes = list(strList.split(","))
    #print(listRes)
    result = []
    for item in strList.strip('][').split(delimiter):
        result.append(item.strip())
    return result

# %% ../nbs/01_putils.ipynb 24
def listNumsToString(list):
    str = ""
    for item in list:
        str += f'{item}'
    return str

# %% ../nbs/01_putils.ipynb 25
def round_lists(alist, formatted, places):    
    if isinstance(alist, str):
        raise Exception(f'Value {alist} should be a number in round_lists.')

    if isinstance(alist, float) or isinstance(alist, int):
        return round(alist,places)
    
    if isinstance(alist[0], float) or isinstance(alist[0], int):
        return [round(num,places) for num in alist]
    else:
        for item in alist:    
            rtd = round_lists(item, formatted, places)
            if rtd is not None:
                formatted.append(rtd)

# %% ../nbs/01_putils.ipynb 26
def floatListsToString(alist, places):
    flist = []    
    round_lists(alist,flist,places)
    return f'{flist}'

# %% ../nbs/01_putils.ipynb 27
def limit_large_float(val, limit=10000000):
    if abs(val) > limit:
        val = - np.sign(val) * limit

    return val

# %% ../nbs/01_putils.ipynb 28
def sigmoid(x, range, slope) :
    val = 0
    if abs(x) > 10000000:
        exv = - np.sign(x) * 10000000
    else:
        exv = -x * slope / range
    if exv > 709:
        exv = 709
    try:
        val = -range / 2 + range / (1 + np.exp(exv))
    except RuntimeWarning:
        print(f'RuntimeWarning... exv={exv} x={x} slope={slope} range={range}')

    return val

# %% ../nbs/01_putils.ipynb 29
def smooth(new_val, old_val, smooth_factor):
    if smooth_factor > 1 or smooth_factor < 0:
        raise Exception(f'smooth_factor {smooth_factor} should be between 0 and 1')
    val = 0
    new_val = limit_large_float(new_val)
    old_val = limit_large_float(old_val)
    try:
        val = old_val * smooth_factor + new_val * (1-smooth_factor)
    except RuntimeWarning:
        print(f'RuntimeWarning... old_val={old_val} new_val={new_val} smooth_factor={smooth_factor}')
    return val

# %% ../nbs/01_putils.ipynb 30
def sigmoid_array(x, range, slope) :
    exv = -x * slope / range
    return -range / 2 + range / (1 + np.exp(exv))
    

# %% ../nbs/01_putils.ipynb 31
def dot(inputs, weights):
    sum = 0
    for i in range(len(inputs)):
        sum += inputs[i]*weights[i]
    return sum

# %% ../nbs/01_putils.ipynb 32
def list_of_ones(num):
    x = [1 for _ in range(num) ]
    return x

# %% ../nbs/01_putils.ipynb 33
def limit_to_range(num, lower, upper):
    if num < lower:
        frac, _  = math.modf(num)
        num = abs(frac)

    if num > upper:
        frac, _ = math.modf(num)
        num = upper - frac
    return num

# %% ../nbs/01_putils.ipynb 35
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

# %% ../nbs/01_putils.ipynb 38
import os

# %% ../nbs/01_putils.ipynb 39
from pathlib import Path

def is_in_notebooks():
    term = os.getenv('TERM') 
    if term == 'xterm-color':
        return True
    
    return False

# %% ../nbs/01_putils.ipynb 40
def printtime(msg):
    print(f'{datetime.now()} {os.getpid()} {msg}')
    return time.perf_counter()


# %% ../nbs/01_putils.ipynb 41
def clip_value(val, range):
    rtn = max(min(val, range[1]), range[0])
    return rtn


# %% ../nbs/01_putils.ipynb 42
def map_to_int_odd_range(val=None, inrange=None, outrange=None):
    a = round(val)
    b = clip_value(a, inrange)
    rtn = b + (int((outrange[1] - outrange[0])/2) + 1)
    return rtn

def map_to_int_even_range(val=None, inrange=None, outrange=None):
    b = clip_value(val, inrange)
    if b == inrange[1]:
        b = b - 1
    rtn = math.floor(b) + int((outrange[1] - outrange[0] + 1 )/2) + 1
    return rtn

# %% ../nbs/01_putils.ipynb 45
class TimerError(Exception):
    """A custom exception used to report errors in use of Timer class"""

class Timer:
    def __init__(self):
        self._start_time = None
        self._counter = 0
        self._total_time = 0

    def start(self):
        """Start a new timer"""
        if self._start_time is not None:
            raise TimerError(f"Timer is running. Use .stop() to stop it")

        self._start_time = time.perf_counter()
        # print(self._start_time)

    def stop(self):
        """Stop the timer, and report the elapsed time"""
        if self._start_time is None:
            raise TimerError(f"Timer is not running. Use .start() to start it")

        elapsed_time = time.perf_counter() - self._start_time 

        self._total_time = self._total_time + elapsed_time
        self._start_time = None
        self._counter += 1
        
    def mean(self):
        mtime = self._total_time / self._counter
        self._start_time = None

        return mtime

    def total(self):
        return self._total_time
    
    def count(self):
        return self._counter 
