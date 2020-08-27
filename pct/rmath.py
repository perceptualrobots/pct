# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/01_utilities.ipynb (unless otherwise specified).

__all__ = ['smooth']

# Cell
def smooth( newVal, oldVal, weight) :
    "An exponential smoothing function. The weight is the smoothing factor applied to the old value."
    return newVal * (1 - weight) + oldVal * weight;