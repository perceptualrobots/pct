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
    def check_list_unchanged(float_list, rel_tol=1e-9, abs_tol=0.0):
        """
        Checks if the list values are unchanged by calculating their gradient, mean, and standard deviation.

        Returns:
            bool: True if the list values are close to each other within the specified tolerance.
            dict: A dictionary containing the gradient, mean, and standard deviation of the list values.
        """
        if not float_list:
            return True, {"gradient": None, "mean": None, "std_dev": None}

        gradient = np.gradient(float_list).mean()
        mean_value = np.mean(float_list)
        std_dev = np.std(float_list)
        first_value = float_list[0]
        # Check if all values are close to the mean
        all_close_to_mean = all(
            math.isclose(value, first_value, rel_tol=rel_tol, abs_tol=abs_tol)
            for value in float_list[1:]
        )

        return all_close_to_mean, {"gradient": gradient, "mean": mean_value, "std_dev": std_dev}

    @staticmethod
    def check_float_list_close_to_zero(float_list, rel_tol=1e-9, abs_tol=0.0, gradient_abs_tol=0.0):
        """
        Checks if the values in the float list are close to zero within the specified tolerance
        and if the gradient (difference between consecutive values) is close to zero within the specified gradient tolerance.

        Returns:
            bool: True if all values are close to zero within the specified tolerance and the gradient of all consecutive values is close to zero within the specified gradient tolerance.
        """
        if not float_list:
            return True
        
        values_close_to_zero = all(
            math.isclose(value, 0, rel_tol=rel_tol, abs_tol=abs_tol)
            for value in float_list
        )
        
        if len(float_list) == 1:
            return values_close_to_zero
        
        gradients_close_to_zero = all(
            math.isclose(float_list[i] - float_list[i - 1], 0, rel_tol=0, abs_tol=gradient_abs_tol)
            for i in range(1, len(float_list))
        )
        
        return values_close_to_zero and gradients_close_to_zero

    @staticmethod
    def check_float_list_close_to_zero1(float_list, rel_tol=1e-9, abs_tol=0.0):
        """
        Checks if the values in the float list are close to zero within the specified tolerance.

        Returns:
            bool: True if all values are close to zero within the specified tolerance.
        """
        if not float_list:
            return True

        gradient = np.gradient(float_list)    
        gradient_mean = gradient.mean()        

        values_close_to_zero = all(
            math.isclose(value, 0, rel_tol=rel_tol, abs_tol=abs_tol)
            for value in float_list
        )

        return values_close_to_zero, gradient_mean, gradient


    @staticmethod
    def check_integer_list_unchanged(int_list):
        """
        Checks if all integers in the list are unchanged (i.e., equal).

        Returns:
            bool: True if all integers are the same.
        """
        if not int_list:
            return True
        first_value = int_list[0]
        for value in int_list:
            if value != first_value:
                return False
        return True






# %% ../nbs/14_helpers.ipynb 12
class JSONDataManager:
    def __init__(self, path: str, show_timing: bool = False):
        self.data = self.load_json(path)
        self.show_timing = show_timing
    
    def load_json(self, path: str) -> Dict:
        with open(path, 'r') as file:
            return json.load(file)
    
    def timing_decorator(method):
        def timed_method(self, *args, **kwargs):
            start_time = time.time()
            result = method(self, *args, **kwargs)
            end_time = time.time()
            if self.show_timing:
                print(f"Execution time of {method.__name__}: {end_time - start_time:.4f} seconds")
            return result
        return timed_method



# %% ../nbs/14_helpers.ipynb 14
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
    
    @JSONDataManager.timing_decorator
    def get_largest_array_size(self) -> Tuple[str, int]:
        max_size = 0
        max_key = ''
        for key, value in self.data.items():
            input_sizes = [np.array(value['train'][iter]['input']).size for iter in range(len(value['train']))]
            output_sizes = [np.array(value['train'][iter]['output']).size for iter in range(len(value['train']))]

            max_input_size = max(input_sizes, default=0)
            max_output_size = max(output_sizes, default=0)
            if max(max_input_size, max_output_size) > max_size:
                max_size = max(max_input_size, max_output_size)
                max_key = key
        return max_key, max_size

    @JSONDataManager.timing_decorator
    def analyze_arrays(self) -> Dict[str, Any]:
        analysis = {
            "equal_input_output": [],
            "consistent_but_different_sizes": [],
            "variable_output_sizes": []
        }
        for key, value in self.data.items():
            input_sizes = [np.array(value['train'][iter]['input']).size for iter in range(len(value['train']))]
            output_sizes = [np.array(value['train'][iter]['output']).size for iter in range(len(value['train']))]
            if all(size == input_sizes[0] for size in input_sizes) and all(size == output_sizes[0] for size in output_sizes):
                if input_sizes[0] == output_sizes[0]:
                    analysis["equal_input_output"].append(key)
                else:
                    analysis["consistent_but_different_sizes"].append(key)
            else:
                analysis["variable_output_sizes"].append(key)
        
        return {
            "analysis": analysis,
            "counts": {k: len(v) for k, v in analysis.items()}
        }



# %% ../nbs/14_helpers.ipynb 16
class SolutionsDataManager(JSONDataManager):
    
    @JSONDataManager.timing_decorator
    def get_all_keys(self) -> List[str]:
        return list(self.data.keys())
    
    @JSONDataManager.timing_decorator
    def count_all_keys(self) -> int:
        return len(self.data)
    
    @JSONDataManager.timing_decorator
    def get_data_for_key(self, key: str) -> Dict[str, Any]:
        data = self.data.get(key, [])
        return data[0] if data else {}
    
    @JSONDataManager.timing_decorator
    def get_arrays_for_key(self, key: str, array_type: str) -> List:
        if key not in self.data or array_type not in self.data[key]:
            return []
        return self.data[key][array_type]



