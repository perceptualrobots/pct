# -*- coding: utf-8 -*-
"""
Created on Sat Sep  5 11:31:58 2020

@author: rupert
"""


#import pct as ppp


from pct.functions import Proportional
p = Proportional()
print(p)


from pct.utilities import FunctionsList

fl = FunctionsList.getInstance()
print(fl)


#fl = ppp.utilities.FunctionsList.getInstance()

import pct.utilities as pu

fl1 = pu.FunctionsList.getInstance()
print(fl1)
