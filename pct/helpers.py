# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/14_helpers.ipynb.

# %% auto 0
__all__ = ['ListChecker', 'JSONDataManager', 'ChallengesDataManager', 'SolutionsDataManager']

# %% ../nbs/14_helpers.ipynb 3
import math
import numpy as np
import json
import time
from collections import Counter
from typing import Any, Dict, List, Tuple


# %% ../nbs/14_helpers.ipynb 5
class ListChecker:
    @staticmethod
    def check_list_unchanged(float_list, rel_tol=1e-6, abs_tol=0.0):
        if not float_list:  # Check if the list is empty
            return True
        first_value = float_list[0]
        for value in float_list[1:]:
            if not math.isclose(value, first_value, rel_tol=rel_tol, abs_tol=abs_tol):
                return False
        return True

    @staticmethod
    def check_integer_list_unchanged(int_list):
        if not int_list:  # Check if the list is empty
            return True
        first_value = int_list[0]
        for value in int_list[1:]:
            if value != first_value:
                return False
        return True


# %% ../nbs/14_helpers.ipynb 7
class JSONDataManager:
    def __init__(self, path: str):
        self.data = self.load_json(path)
    
    def load_json(self, path: str) -> Dict:
        with open(path, 'r') as file:
            return json.load(file)
    
    def timing_decorator(method):
        def timed_method(*args, **kwargs):
            start_time = time.time()
            result = method(*args, **kwargs)
            end_time = time.time()
            print(f"Execution time of {method.__name__}: {end_time - start_time:.4f} seconds")
            return result
        return timed_method



# %% ../nbs/14_helpers.ipynb 8
class ChallengesDataManager(JSONDataManager):
    
    @JSONDataManager.timing_decorator
    def get_all_keys(self) -> List[str]:
        return list(self.data.keys())
    
    @JSONDataManager.timing_decorator
    def count_all_keys(self) -> int:
        return len(self.data)
    
    @JSONDataManager.timing_decorator
    def get_keys_with_equal_size_input_output(self) -> Tuple[List[str], int]:
        equal_keys = [
            key for key, value in self.data.items()
            if all(len(value['train'][iter]['input']) == len(value['train'][iter]['output']) for iter in range(len(value['train'])))
        ]
        return equal_keys, len(equal_keys)
    
    @JSONDataManager.timing_decorator
    def get_keys_with_inconsistent_input_output_sizes(self) -> Tuple[List[str], int]:
        inconsistent_keys = []
        for key, value in self.data.items():
            input_sizes = [len(value['train'][iter]['input']) for iter in range(len(value['train']))]
            output_sizes = [len(value['train'][iter]['output']) for iter in range(len(value['train']))]
            if len(set(input_sizes)) == 1 and len(set(output_sizes)) == 1 and input_sizes[0] < output_sizes[0]:
                inconsistent_keys.append(key)
        return inconsistent_keys, len(inconsistent_keys)
    
    @JSONDataManager.timing_decorator
    def get_keys_with_variable_input_sizes(self) -> Tuple[List[str], int]:
        variable_keys = [
            key for key, value in self.data.items()
            if len(set(len(value['train'][iter]['input']) for iter in range(len(value['train'])))) > 1
            # if len(set(len(arr) for arr in value['train']['input'])) > 1
        ]
        return variable_keys, len(variable_keys)
    
    @JSONDataManager.timing_decorator
    def get_input_array_histogram(self) -> Dict[int, int]:
        counts = Counter(len(value['train']) for value in self.data.values())
        return dict(counts)
    
    @JSONDataManager.timing_decorator
    def get_data_for_key(self, key: str) -> Dict[str, Any]:
        return self.data.get(key, {})
    
    @JSONDataManager.timing_decorator
    def get_arrays_for_key(self, key: str, array_type: str) -> List:
        if key not in self.data or 'train' not in self.data[key] or array_type not in self.data[key]['train']:
            return []
        return self.data[key]['train'][array_type]
    



# %% ../nbs/14_helpers.ipynb 9
class SolutionsDataManager(JSONDataManager):
    
    @JSONDataManager.timing_decorator
    def get_all_keys(self) -> List[str]:
        return list(self.data.keys())
    
    @JSONDataManager.timing_decorator
    def count_all_keys(self) -> int:
        return len(self.data)
    
    @JSONDataManager.timing_decorator
    def get_data_for_key(self, key: str) -> Dict[str, Any]:
        rtn = self.data.get(key, {})
        return rtn[0]
    
    @JSONDataManager.timing_decorator
    def get_arrays_for_key(self, key: str, array_type: str) -> List:
        if key not in self.data or array_type not in self.data[key]:
            return []
        return self.data[key][array_type]


