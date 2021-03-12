# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/07_errors.ipynb (unless otherwise specified).

__all__ = ['BaseErrorType', 'RootSumSquaredError', 'RootMeanSquareError', 'CurrentError', 'SmoothError',
           'BaseErrorCollector', 'TotalError', 'TopError', 'InputsError', 'ReferencedInputsError', 'RewardError',
           'ErrorFactory']

# Cell
import numpy as np
from abc import ABC, abstractmethod
from .hierarchy import PCTHierarchy
from .functions import IndexedParameter
from .putils import smooth

# Cell
class BaseErrorType(ABC):
    "Base class of a type error response. This class is not used direclty by developers, but defines the interface common to all."
    def __init__(self):
        self.error_response=0

    @abstractmethod
    def __call__(self):
        pass

    def set_property(self, property_name, property_value):
        exec(f'self.{property_name} = {property_value}')

    def get_error_response(self):
        return self.error_response

# Cell
class RootSumSquaredError(BaseErrorType):
    "The square root of the sum of the square of the errors."
    def __init__(self):
        super().__init__()
        self.sum=0

    def __call__(self, error):
        self.sum+=error*error
        self.error_response=np.sqrt(self.sum)

    class Factory:
        def create(self): return RootSumSquaredError()

# Cell
class RootMeanSquareError(BaseErrorType):
    "The square root of the sum of the square of the errors."
    def __init__(self):
        super().__init__()
        self.sum=0
        self.num=0

    def __call__(self, error):
        self.num+=1
        self.sum+=error*error
        self.error_response=np.sqrt(self.sum/self.num)

    class Factory:
        def create(self): return RootMeanSquareError()

# Cell
class CurrentError(BaseErrorType):
    "The current error, rather than a function of the historical values."
    def __init__(self):
        super().__init__()

    def __call__(self, error):
        self.error_response=error

    class Factory:
        def create(self): return CurrentError()

# Cell
class SmoothError(BaseErrorType):
    "The exponential smoothed value of the error."
    def __init__(self):
        super().__init__()
        self.smooth_factor = None

    def __call__(self, error):
        self.error_response=smooth(abs(error), self.error_response, self.smooth_factor)

    class Factory:
        def create(self): return SmoothError()

# Cell
class BaseErrorCollector(ABC):
    "Base class of an error collector. This class is not used direclty by developers, but defines the interface common to all."
    'Parameters:'
    'limit - the limit of valid error response'
    'error_response - the type of error response'

    def __init__(self, limit,error_response):
        self.limit=limit
        self.limit_exceeded=False
        self.error_response=error_response

    def set_limit(self, limit):
        self.limit=limit
        self.limit_exceeded=False

    def set_error_response(self, error_response):
        self.error_response=error_response

    def error(self):
        return self.error_response.get_error_response()

    def add_error_data(self, data=[]):
        for datum in data:
            self.error_response(datum)

    def is_limit_exceeded(self):
        return self.limit_exceeded

    @classmethod
    def collector(cls, error_response_type, error_collector_type, limit, properties=None):
        error_response = ErrorFactory.createError(error_response_type)
        error_collector = ErrorFactory.createError(error_collector_type)
        ec.set_limit(limit)

        if properties != None:
            for property in properties:
                if error_response_type == 'SmoothError' and property[0] == 'smooth_factor':
                    error_response.set_property(property[0], property[1])
                    continue
                if error_collector_type == 'ReferencedInputsError' and property[0] == 'referenced_inputs':
                    error_collector.set_reference_properties(property[1]):
                    continue

        error_collector.set_error_response(error_response)

        return error_collector

# Cell
class TotalError(BaseErrorCollector):
    "A class to collect all the errors of the control system run."
    def __init__(self, limit=1000, error_response=None, **cargs):
        super().__init__(limit, error_response)

    def add_data(self, hpct=None):
        for level in range(len(hpct.hierarchy)):
             for col in range(len(hpct.hierarchy[level])):
                node  = hpct.hierarchy[level][col]
                self.add_error_data( [node.get_function("comparator").get_value()])
                if self.error_response.get_error_response() > self.limit:
                    self.limit_exceeded=True
                    return
    class Factory:
        def create(self): return TotalError()

# Cell
class TopError(BaseErrorCollector):
    "A class to collect all the errors of the top-level nodes."
    def __init__(self, limit=1000, error_response=None, **cargs):
        super().__init__(limit, error_response)

    def add_data(self, hpct=None):
        level = len(hpct.hierarchy)-1

        for col in range(len(hpct.hierarchy[level])):
            node  = hpct.hierarchy[level][col]
            self.add_error_data( [node.get_function("comparator").get_value()])
            if self.error_response.get_error_response() > self.limit:
                self.limit_exceeded=True
                return

    class Factory:
        def create(self): return TopError()

# Cell
class InputsError(BaseErrorCollector):
    "A class to collect the values of the input values."
    def __init__(self, limit=1000, error_response=None, **cargs):
        super().__init__(limit, error_response)

    def add_data(self, hpct=None):
        data = []
        pre = hpct.get_preprocessor()
        for func in pre:
            if isinstance(func, IndexedParameter):
                data.append(func.get_value())
        self.add_error_data( data )
        if self.error_response.get_error_response() > self.limit:
            self.limit_exceeded=True
            return
    class Factory:
        def create(self): return InputsError()

# Cell
class ReferencedInputsError(BaseErrorCollector):
    "A class to collect the values of the input values subtracted from reference values."
    def __init__(self, limit=1000, error_response=None, **cargs):
        super().__init__(limit, error_response)
        self.reference_values=None
        self.input_indexes=None


    def set_reference_properties(properties):
        strarr = properties.split(':')
        self.reference_values=[]
        self.input_indexes=[]

        for inp in strarr[0].split(';')
            self.input_indexes.append(eval(inp))

        for ref in strarr[1].split(';')
            self.reference_values.append(eval(ref))


    def add_data(self, hpct=None):
        data = []
        pre = hpct.get_preprocessor()
        for ctr, index enumerate():
            func = pre[index+1]
            if isinstance(func, IndexedParameter):
                data.append(self.reference_values[ctr]-func.get_value())
            else:
                raise Exception(f'Function {func.get_name()} is not type IndexedParameter.')
        self.add_error_data( data )
        if self.error_response.get_error_response() > self.limit:
            self.limit_exceeded=True
            return
    class Factory:
        def create(self): return ReferencedInputsError()

# Cell
class RewardError(BaseErrorCollector):
    "A class that collects the reward value of the control system run."
    def __init__(self, limit=1000, error_response=None, **cargs):
        super().__init__(limit, error_response)

    def add_data(self, hpct=None):
        data = []
        pre = hpct.get_preprocessor()
        data.append(pre[0].get_reward())
        self.add_error_data( data )
        if self.error_response.get_error_response() > self.limit:
            self.limit_exceeded=True
            return
    class Factory:
        def create(self): return RewardError()

# Cell
class ErrorFactory:
    factories = {}
    def addFactory(id, errorFactory):
        ErrorFactory.factories.put[id] = errorFactory
    addFactory = staticmethod(addFactory)
    # A Template Method:
    def createError(id):
        if not ErrorFactory.factories.__contains__(id):
            ErrorFactory.factories[id] = \
              eval(id + '.Factory()')
        return ErrorFactory.factories[id].create()
    createError = staticmethod(createError)