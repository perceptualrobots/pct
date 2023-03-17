# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/10_webots.ipynb.

# %% auto 0
__all__ = ['WebotsHelper']

# %% ../nbs/10_webots.ipynb 1
class WebotsHelper():
    
    def __init__(self, name=None, mode=1):
        self.name = name
        self.mode = mode
        if self.mode==1:
            self.num_inputs=6

    def get_inputs_indexes(self):
        if self.mode==1:
            return [i for i in range(self.num_inputs)]
        
        
    def get_inputs_names(self):
        if self.mode==1:
            return [ 'LHipPitch', 'LKneePitch', 'LAnklePitch', 'RHipPitch', 'RKneePitch', 'RAnklePitch']
    
    def get_references(self):
        if self.mode==1:
            return [i for i in range(self.num_inputs)]
        
