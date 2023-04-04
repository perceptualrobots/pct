# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/07_errors.ipynb.

# %% auto 0
__all__ = ['BaseErrorType', 'RootSumSquaredError', 'RootMeanSquareError', 'CurrentError', 'SmoothError', 'BaseErrorCollector',
           'TotalError', 'TopError', 'InputsError', 'ReferencedInputsError', 'RewardError', 'ErrorResponseFactory',
           'ErrorCollectorFactory']

# %% ../nbs/07_errors.ipynb 3
#import numpy as np
import math
from abc import ABC, abstractmethod
from .functions import IndexedParameter
from .putils import smooth

# %% ../nbs/07_errors.ipynb 5
class BaseErrorType(ABC):
    "Base class of a type error response. This class is not used direclty by developers, but defines the interface common to all."
    def __init__(self, flip_error_response=False):
        self.factor=1
        if flip_error_response:
            self.factor=-1
        self.error_response=None
        
    def __repr__(self):
        if self.error_response == None:
            return f': {self.__class__.__name__} error_response:{self.error_response}'
        return f': {self.__class__.__name__} error_response:{self.error_response * self.factor}'

    
    @abstractmethod
    def __call__(self):
        pass
    
    @abstractmethod
    def reset(self):
        self.error_response=None

    def set_property(self, property_name, property_value):
        exec(f'self.{property_name} = {property_value}')
        
    def get_error_response(self):
        return self.error_response * self.factor
    
    def set_error_response(self, error):
        self.error_response = error * self.factor
        

# %% ../nbs/07_errors.ipynb 6
class RootSumSquaredError(BaseErrorType):
    "The square root of the sum of the square of the errors."
    def __init__(self, flip_error_response=False):
        super().__init__(flip_error_response=flip_error_response)
        self.sum=0
        
    def __call__(self, error):
        self.sum+=error*error
        self.error_response=math.sqrt(self.sum)

    def reset(self):
        super().reset()
        self.sum=0
        
    class Factory:
        def create(self, flip_error_response=False): return RootSumSquaredError(flip_error_response=flip_error_response)

# %% ../nbs/07_errors.ipynb 7
class RootMeanSquareError(BaseErrorType):
    "The square root of the mean of the sum of the square of the errors."
    def __init__(self, flip_error_response=False):
        super().__init__(flip_error_response=flip_error_response)
        self.reset()
        
    def __call__(self, error):
        self.num+=1
        self.sum+=error*error
        self.error_response=math.sqrt(self.sum/self.num)

    def reset(self):
        super().reset()
        self.sum=0
        self.num=0
        
    class Factory:
        def create(self, flip_error_response=False): return RootMeanSquareError(flip_error_response=flip_error_response)

# %% ../nbs/07_errors.ipynb 8
class CurrentError(BaseErrorType):
    "The current error, rather than a function of the historical values."
    def __init__(self, flip_error_response=False):
        super().__init__(flip_error_response=flip_error_response)
    
    def __call__(self, error):
        self.error_response=error

    def reset(self):
        super().reset()

    class Factory:
        def create(self, flip_error_response=False): return CurrentError(flip_error_response=flip_error_response)

# %% ../nbs/07_errors.ipynb 9
class SmoothError(BaseErrorType):
    "The exponential smoothed value of the error."
    def __init__(self, flip_error_response=False):
        super().__init__(flip_error_response=flip_error_response)        
        self.smooth_factor = None
        self.error_response = 0
    
    def __call__(self, error):
        self.error_response=smooth(abs(error), self.error_response, self.smooth_factor)
        
    def reset(self):
        self.error_response = 0

    class Factory:
        def create(self, flip_error_response=False): return SmoothError(flip_error_response=flip_error_response)

# %% ../nbs/07_errors.ipynb 10
class BaseErrorCollector(ABC):
    "Base class of an error collector. This class is not used direclty by developers, but defines the interface common to all."
    'Parameters:'
    'limit - the limit of valid error response'
    'error_response - the type of error response'
    
    def __init__(self, limit,error_response, min):
        self.limit=limit
        self.limit_exceeded=False
        self.error_response=error_response
        self.min=min

        
    def __repr__(self):
        return f'{self.__class__.__name__} limit:{self.limit}, limit_exceeded:{self.limit_exceeded}, {self.error_response.__repr__()}'
        
    def set_min(self, min):
        self.min=min

    def set_limit(self, limit):
        self.limit=limit
        self.limit_exceeded=False

    def set_error_response(self, error_response):
        self.error_response=error_response
    
    def reset(self):
        self.error_response.reset()

    def error(self):
        return self.error_response.get_error_response()

    def override_value(self):
        self.error_response.set_error_response(self.error_response.get_error_response()*abs(self.limit))

#     def set_maximum(self):
#         self.error_response.set_error_response(self.limit)
    
    def add_error_data(self, data=[]):
        for datum in data:
            self.error_response(datum)
                  
    def is_limit_exceeded(self):            
        return self.limit_exceeded        
    
    @classmethod
    def collector(cls, error_response_type, error_collector_type, limit, min, properties=None, flip_error_response=False):
        error_response = ErrorResponseFactory.createErrorResponse(error_response_type, flip_error_response=flip_error_response)   
        error_collector = ErrorCollectorFactory.createErrorCollector(error_collector_type)   
        error_collector.set_limit(limit)
        error_collector.set_min(min)
        
        if properties != None:
            for property in properties:
                if error_response_type == 'SmoothError' and property[0] == 'smooth_factor':
                    error_response.set_property(property[0], property[1])
                    continue
                if error_collector_type == 'ReferencedInputsError' and property[0] == 'referenced_inputs':
                    error_collector.set_reference_properties(property[1])
                    continue
            
        error_collector.set_error_response(error_response)
        
        return error_collector
    
    def check_limit(self):
        if self.min:
            if self.error_response.get_error_response() > self.limit:
                self.limit_exceeded=True
        else:
            if self.error_response.get_error_response() < self.limit:
                self.limit_exceeded=True
        
        return self.limit_exceeded

# %% ../nbs/07_errors.ipynb 11
class TotalError(BaseErrorCollector):
    "A class to collect all the errors of the control system run."            
    def __init__(self, limit=1000, error_response=None, min=None, **cargs):
        super().__init__(limit, error_response, min)

    def add_data(self, hpct=None):
        for level in range(len(hpct.hierarchy)):
             for col in range(len(hpct.hierarchy[level])):
                node  = hpct.hierarchy[level][col]
                self.add_error_data( [node.get_function("comparator").get_value()])
                if self.check_limit():
#                 if self.error_response.get_error_response() > self.limit:
#                     self.limit_exceeded=True
                    return
    class Factory:
        def create(self): return TotalError()

# %% ../nbs/07_errors.ipynb 12
class TopError(BaseErrorCollector):
    "A class to collect all the errors of the top-level nodes."            
    def __init__(self, limit=1000, error_response=None, min=None, **cargs):
        super().__init__(limit, error_response, min)

    def add_data(self, hpct=None):
        level = len(hpct.hierarchy)-1
            
        for col in range(len(hpct.hierarchy[level])):
            node  = hpct.hierarchy[level][col]
            self.add_error_data( [node.get_function("comparator").get_value()])
            if self.check_limit():
#             if self.error_response.get_error_response() > self.limit:
#                 self.limit_exceeded=True
                return
            
    class Factory:
        def create(self): return TopError()

# %% ../nbs/07_errors.ipynb 13
class InputsError(BaseErrorCollector):
    "A class to collect the values of the input values."            
    def __init__(self, limit=1000, error_response=None, min=None, **cargs):
        super().__init__(limit, error_response, min)

    def add_data(self, hpct=None):
        data = []
        pre = hpct.get_preprocessor()
        for func in pre:
            if isinstance(func, IndexedParameter):
                data.append(func.get_value())
        self.add_error_data( data )
        if self.check_limit():
#         if self.error_response.get_error_response() > self.limit:
#             self.limit_exceeded=True
            return
        
    class Factory:
        def create(self): return InputsError()

# %% ../nbs/07_errors.ipynb 14
class ReferencedInputsError(BaseErrorCollector):
    "A class to collect the values of the input values subtracted from reference values."                        
    def __init__(self, limit=1000, error_response=None, min=None, **cargs):
        super().__init__(limit, error_response, min)
        self.reference_values=None
        self.input_indexes=None        
        
    def set_reference_properties(self, properties):
        strarr = properties.split('&')        
        self.reference_values=[]
        self.input_indexes=[]

        for inp in strarr[0].split(';'):
            self.input_indexes.append(eval(inp))
        
        for ref in strarr[1].split(';'):
            self.reference_values.append(eval(ref))
                

    def add_data(self, hpct=None):
        data = []
        pre = hpct.get_preprocessor()
        for ctr, index in enumerate(self.input_indexes):
            func = pre[index+1] # add 1 as environment is 0
            if isinstance(func, IndexedParameter):
                data.append(self.reference_values[ctr]-func.get_value())
            else:
                raise Exception(f'Function {func.get_name()} is not type IndexedParameter.')
        self.add_error_data( data )
        if self.check_limit():
#         if self.error_response.get_error_response() > self.limit:
#             self.limit_exceeded=True
            return

    class Factory:
        def create(self): return ReferencedInputsError()

# %% ../nbs/07_errors.ipynb 15
class RewardError(BaseErrorCollector):
    "A class that collects the reward value of the control system run."            
    def __init__(self, limit=1000, error_response=None, min=None, **cargs):
        super().__init__(limit, error_response, min)

    def add_data(self, hpct=None):
        data = []
        pre = hpct.get_preprocessor()
        data.append(pre[0].get_reward())
        self.add_error_data( data )
        if self.check_limit():
#         if self.error_response.get_error_response() > self.limit:
#             self.limit_exceeded=True
            return
    class Factory:
        def create(self): return RewardError()

# %% ../nbs/07_errors.ipynb 16
class ErrorResponseFactory:
    factories = {}
    def addResponseFactory(id, errorResponseFactory):
        ErrorResponseFactory.factories.put[id] = errorFactory
    addResponseFactory = staticmethod(addResponseFactory)
    # A Template Method:
    def createErrorResponse(id, flip_error_response=False):
        if not ErrorResponseFactory.factories.__contains__(id):
            ErrorResponseFactory.factories[id] = \
              eval(id + '.Factory()')
        return ErrorResponseFactory.factories[id].create(flip_error_response=flip_error_response)
    createErrorResponse = staticmethod(createErrorResponse)

# %% ../nbs/07_errors.ipynb 17
class ErrorCollectorFactory:
    factories = {}
    def addCollectorFactory(id, errorCollectorFactory):
        ErrorCollectorFactory.factories.put[id] = errorFactory
    addCollectorFactory = staticmethod(addCollectorFactory)
    # A Template Method:
    def createErrorCollector(id):
        if not ErrorCollectorFactory.factories.__contains__(id):
            ErrorCollectorFactory.factories[id] = \
              eval(id + '.Factory()')
        return ErrorCollectorFactory.factories[id].create()
    createErrorCollector = staticmethod(createErrorCollector)
