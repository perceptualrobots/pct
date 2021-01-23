# Perceptual Control Theory
> A python library for creating perceptual control hierarchies.


With this library you can create and run simple or complex hierarchies of perceptual control systems as well as make use of the power of the Python platform and its rich set of packages.

In the context of this library a single control system comprising a perceptual, reference, comparator and output function is called a Node. The functions therein can be configured by the user.

A hierarchy is defined by a collection of nodes.

## Install

`pip install pct`

## Import

Examples of importing the library functionality.

`import pct as p`

`from pct.hierarchy import Hierarchy`

`from pct import *`

## How to use

Import modules from the PCT library.

```
from pct.nodes import PCTNode
```

For the purposes of this example define a world model. This would not be required if the real world is used, or a simulation such as OpenAI Gym.

```
def velocity_model(velocity,  force , mass):
    velocity = velocity + force / mass
    return velocity

# World value
mass = 50
```

Create a PCTNode, a control system unit comprising a reference, perception, comparator and output function. The default value for the reference is 1. With the history flag set, the data for each iteration is recorded for later plotting. 

```
pctnode = PCTNode(history=True)
```

Call the node repeatedly to control the perception of velocity. With the verbose flag set, the control values are printed. In this case the printed values are the iteration number, the (velocity) reference, the perception, the error and the (force) output.

```
for i in range(40):
    print(i, end=" ")
    force = pctnode(verbose=True)
    velocity = velocity_model(pctnode.get_perception_value(), force, mass)
    pctnode.set_perception_value(velocity)
```

    0 1.000 0.000 1.000 


    ---------------------------------------------------------------------------

    Exception                                 Traceback (most recent call last)

    <ipython-input-5-49aa7ec3e15c> in <module>
          1 for i in range(40):
          2     print(i, end=" ")
    ----> 3     force = pctnode(verbose=True)
          4     velocity = velocity_model(pctnode.get_perception_value(), force, mass)
          5     pctnode.set_perception_value(velocity)


    /mnt/c/Users/ruper/Versioning/python/nbdev/pct/pct/nodes.py in __call__(self, verbose)
         78 
         79         for outputFunction in self.outputCollection:
    ---> 80             outputFunction(verbose)
         81 
         82         self.output = self.outputCollection[-1].get_value()


    /mnt/c/Users/ruper/Versioning/python/nbdev/pct/pct/functions.py in __call__(self, verbose)
        569     def __call__(self, verbose=False):
        570         if len(self.links) != self.weights.size:
    --> 571             raise Exception(f'Number of links {len(self.links)} and weights {self.weights.size} must be the same.')
        572 
        573         super().check_links(len(self.links))


    Exception: Number of links 1 and weights 3 must be the same.


Using the plotly library plot the data. The graph shows the perception being controlled to match the reference value.

```python
import plotly.graph_objects as go
fig = go.Figure(layout_title_text="Velocity Goal")
fig.add_trace(go.Scatter(y=pctnode.history.data['refcoll']['constant'], name="ref"))
fig.add_trace(go.Scatter(y=pctnode.history.data['percoll']['variable'], name="perc"))
```

This following code is only for the purposes of displaying image of the graph generated by the above code.

```
from IPython.display import Image
Image(url='http://www.perceptualrobots.com/wp-content/uploads/2020/08/pct_node_plot.png') 
```

This shows a very basic example of the use of the PCT library. For more advanced functionality see the API documentation at https://perceptualrobots.github.io/pct/.
