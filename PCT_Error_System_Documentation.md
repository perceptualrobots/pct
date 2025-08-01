# PCT Error Collection and Response System

This document explains the error collection and response system for Perceptual Control Theory (PCT) hierarchies defined in the `07_errors.ipynb` notebook.

## Overview

The error system consists of two main components:
1. **Error Response Classes** - Define how to aggregate/calculate errors over time
2. **Error Collection Classes** - Define which errors to collect from the PCT hierarchy

## Error Response Classes (How to Calculate Error)

These classes define different ways to aggregate errors over time:

### BaseErrorType (Abstract Base)
- Interface for all error response types
- Handles error flipping (multiply by -1 if needed)
- Manages termination states

### Specific Error Response Types

#### 1. RootSumSquaredError
```python
# √(∑error²)
# Square root of sum of squared errors
# Accumulates error magnitude over time
```

#### 2. RootMeanSquareError  
```python
# √(mean(∑error²))
# RMS of errors over time, normalized by count
# Uses NumPy's linalg.norm() for vector errors
```

#### 3. SummedError
```python
# ∑error
# Simple accumulation of all errors
```

#### 4. CurrentError
```python
# error_current
# Just uses the most recent error value
```

#### 5. CurrentRMSError
```python
# √(mean(error_array²))
# RMS of current error array (not historical)
```

#### 6. SmoothError
```python
# Exponentially smoothed error
# Uses smoothing factor to blend current with historical
# Configurable smooth_factor parameter
```

#### 7. MovingSumError / MovingAverageError
```python
# Moving window sum/average of recent errors
# Uses a "boxcar" (sliding window) approach
# Configurable history parameter
```

## Error Collection Classes (What Errors to Collect)

These classes define which errors to collect from the PCT hierarchy:

### BaseErrorCollector (Abstract Base)
- Interface for all error collectors
- Manages error limits and termination conditions
- Combines with error response types via factory pattern

### Specific Error Collectors

#### 1. TotalError
- Collects errors from **all comparator nodes** in the hierarchy
- Most comprehensive error collection
- Iterates through all levels and columns

#### 2. TopError
- Collects errors only from **top-level nodes**
- Focuses on highest-level control errors
- Only examines the highest hierarchy level

#### 3. InputsError
- Collects **input values** from preprocessors
- Can specify which input indexes to monitor via properties
- Configurable `indexes` parameter

#### 4. ReferencedInputsError
- Collects **(reference - input)** differences
- Weighted differences from target reference values
- Requires configuration:
  - `indexes`: which inputs to monitor
  - `refs`: reference values for each input
  - `weights`: weighting factors

#### 5. RewardError / FitnessError
- Collects reward/fitness values from the environment
- For reinforcement learning scenarios
- Accesses environment's reward/fitness methods

## Factory Pattern

The system uses factory patterns for dynamic object creation:

### ErrorResponseFactory
```python
# Creates error response objects dynamically
error_response = ErrorResponseFactory.createErrorResponse('RootMeanSquareError')
```

### ErrorCollectorFactory  
```python
# Creates error collector objects dynamically
collector = ErrorCollectorFactory.createErrorCollector('InputsError')
```

### Combined Factory Method
```python
# Convenience method that combines both
collector = BaseErrorCollector.collector(
    'RootMeanSquareError',  # How to calculate
    'InputsError',          # What to collect
    limit=10,               # Termination threshold
    min=False,              # Terminate when BELOW limit
    properties={'error_response': {'smooth_factor': 0.9}}
)
```

## Usage Examples

### Basic Error Collection
```python
# Create an RMS error collector for input monitoring
collector = BaseErrorCollector.collector(
    'RootMeanSquareError',
    'InputsError', 
    limit=10,
    min=False  # Terminate when error drops below 10
)

# During PCT hierarchy execution
collector.add_data(hierarchy)  # Collect current errors
if collector.is_terminated():  # Check termination condition
    break
```

### Advanced Configuration
```python
# Smooth error with custom smoothing factor
smooth_collector = BaseErrorCollector.collector(
    'SmoothError',
    'InputsError',
    limit=5,
    min=False,
    properties={
        'error_response': {'smooth_factor': 0.9}
    }
)

# Referenced inputs with custom references and weights
ref_collector = BaseErrorCollector.collector(
    'RootMeanSquareError',
    'ReferencedInputsError',
    limit=1.0,
    min=False,
    properties={
        'error_collector': {
            'referenced_inputs': {
                'indexes': [0, 1, 2],      # Monitor inputs 0, 1, 2
                'refs': [10, 20, 30],      # Target values
                'weights': [1.0, 2.0, 1.5] # Importance weights
            }
        }
    }
)
```

### Moving Window Errors
```python
# Moving average over last 10 time steps
moving_collector = BaseErrorCollector.collector(
    'MovingAverageError',
    'TotalError',
    limit=5.0,
    min=False,
    properties={
        'error_response': {
            'history': 10,    # Window size
            'initial': 0.0    # Initial value to fill window
        }
    }
)
```

## Error Response Examples from Notebook

### Root Mean Square Error
```python
rms = RootMeanSquareError()
for i in range(10):
    rms([i])
er = rms.get_error_response()
# Result: 5.338539126015656
```

### Root Sum Squared Error
```python
rsse = RootSumSquaredError()
te = TotalError(error_response=rsse, limit=250, min=True)   
te.add_error_data([1, 2])
err = te.error()
# Result: 2.23606797749979
```

### Current RMS Error
```python
ip_curr_rms = BaseErrorCollector.collector(
    'CurrentRMSError', 'InputsError', 10, 
    flip_error_response=False, min=False
)
data = [4, 5, 6]
ip_curr_rms.add_error_data_array(data)
rms = ip_curr_rms.error()
# Result: 5.066228051190222
```

### Smooth Error
```python
ins_sm = BaseErrorCollector.collector(
    'SmoothError', 'InputsError', 10, 
    flip_error_response=False, min=False, 
    properties={'error_response': {'smooth_factor': 0.9}}
)
# Process time series data...
# Result shows exponentially smoothed values
```

## Termination Logic

- **min=True**: Terminate when error **exceeds** limit (error > limit)
- **min=False**: Terminate when error **falls below** limit (error < limit)
- **limit_exceeded**: Boolean flag indicating termination
- **flip_error_response**: Multiply error by -1 (useful for maximization problems)

## Key Benefits

1. **Flexible Error Monitoring**: Choose what errors to track and how to aggregate them
2. **Configurable Termination**: Set custom thresholds and termination conditions  
3. **Modular Design**: Mix and match response types with collection strategies
4. **Real-time Monitoring**: Check termination conditions during hierarchy execution
5. **Scientific Reproducibility**: Consistent error calculation for experiments
6. **Vector Support**: Handle both scalar and vector error values
7. **Historical Analysis**: Support for moving windows and exponential smoothing

## Common Use Cases

### 1. Control System Optimization
```python
# Monitor total system error with RMS aggregation
total_rms = BaseErrorCollector.collector(
    'RootMeanSquareError', 'TotalError', 
    limit=1.0, min=False
)
```

### 2. Input Tracking
```python
# Track specific inputs with current RMS
input_tracker = BaseErrorCollector.collector(
    'CurrentRMSError', 'InputsError',
    limit=5.0, min=False,
    properties={'error_collector': {'indexes': [0, 2, 4]}}
)
```

### 3. Reference Following
```python
# Monitor reference tracking with weighted errors
ref_tracker = BaseErrorCollector.collector(
    'RootMeanSquareError', 'ReferencedInputsError',
    limit=2.0, min=False,
    properties={
        'error_collector': {
            'referenced_inputs': {
                'indexes': [0, 1],
                'refs': [10.0, -5.0],
                'weights': [1.0, 2.0]
            }
        }
    }
)
```

### 4. Reinforcement Learning
```python
# Monitor reward/fitness for RL applications
reward_monitor = BaseErrorCollector.collector(
    'SmoothError', 'RewardError',
    limit=100.0, min=True,  # Terminate when reward exceeds 100
    properties={'error_response': {'smooth_factor': 0.95}}
)
```

This comprehensive error system provides the foundation for robust PCT control system monitoring, optimization, and automated termination based on performance criteria.
