# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_nodes.ipynb (unless otherwise specified).

__all__ = ['PCTNode', 'PCTNodeData']

# Cell
import networkx as nx
import json
import matplotlib.pyplot as plt
from .putils import UniqueNamer
from .putils import FunctionsList
from .functions import *
from .environments import *

# Cell
class PCTNode():
    "A single PCT controller."
    def __init__(self, reference=None, perception=None, comparator=None, output=None, default=True,
                 name="pctnode", history=False, build_links=False, mode=0, **pargs):
        # mode
        # 0 - per:var, ref:con, com:sub, out:prop
        # 1 - per:ws, ref:ws, com:sub, out:prop
        # 2 - per:ws, ref:con, com:sub, out:prop
        # 3 - per:ws, ref:ws, com:sub, out:ws
        # 4 - per:ws, ref:con, com:sub, out:ws
        # 5 - per:ws, ref:con, com:sub, out:smws
        # 6 - per:ws, ref:ws, com:sub, out:smws

        self.links_built = False
        self.history = None
        if history:
            self.history = PCTNodeData()
        self.name = UniqueNamer.getInstance().get_name(name)
        FunctionsList.getInstance().add_function(self)
        if default:
            if perception==None:
                if mode >0 :
                     perception =  WeightedSum()
                else:
                     perception =  Variable(0)
            self.perceptionCollection = [perception]

            if reference==None:
                if mode == 1 or mode == 3 or mode == 6:
                    reference =  WeightedSum()
                elif mode ==0 or mode == 2 or mode == 4 or mode == 5:
                    reference = Constant(1)
            self.referenceCollection = [reference]

            if comparator==None:
                comparator = Subtract()
            self.comparatorCollection = [comparator]

            if output==None:
                if mode >2 and mode < 5:
                    output =  WeightedSum()
                elif mode == 6:
                    output =  SmoothWeightedSum()
                else:
                    output = Proportional(10)

            self.outputCollection = [output]

            if build_links:
                self.build_links()

    def __call__(self, verbose=False):
        if not self.links_built:
            self.build_links()

        for referenceFunction in self.referenceCollection:
            referenceFunction(verbose)

        for perceptionFunction in self.perceptionCollection:
            perceptionFunction(verbose)

        for comparatorFunction in self.comparatorCollection:
            comparatorFunction(verbose)

        for outputFunction in self.outputCollection:
            outputFunction(verbose)

        self.output = self.outputCollection[-1].get_value()

        if verbose:
            print()

        if not self.history == None:
            self.history.add_data(self)

        return self.output

    def get_name(self):
        return self.name

    def get_function(self, collection, position=-1):
        if collection == "reference":
            func = self.referenceCollection[position]

        if collection == "perception":
            func = self.perceptionCollection[position]

        if collection == "comparator":
            func = self.comparatorCollection[position]

        if collection == "output":
            func = self.outputCollection[position]

        return func

    def get_perception_value(self, position=-1):
        return self.perceptionCollection[position].get_value()

    def set_perception_value(self, value, position=-1):
        self.perceptionCollection[position].set_value(value)

    def add_link(self, collection, link):
        if collection == "reference":
            self.referenceCollection[0].add_link(link)

        if collection == "perception":
            self.perceptionCollection[0].add_link(link)

        if collection == "comparator":
            self.comparatorCollection[-1].add_link(link)

        if collection == "output":
            self.outputCollection[-1].add_link(link)

    def build_links(self):
        if len(self.referenceCollection)>0:
            link = self.referenceCollection[0]
            for i in range (1, len(self.referenceCollection)):
                self.referenceCollection[i].add_link(link)
                link = self.referenceCollection[i]

        if len(self.perceptionCollection)>0:
            link = self.perceptionCollection[0]
            for i in range (1, len(self.perceptionCollection)):
                self.perceptionCollection[i].add_link(link)
                link = self.perceptionCollection[i]

        self.comparatorCollection[0].add_link(self.referenceCollection[-1])
        self.comparatorCollection[0].add_link(self.perceptionCollection[-1])

        if len(self.comparatorCollection)>1:
            link = self.comparatorCollection[1]
            for i in range (1, len(self.comparatorCollection)):
                self.comparatorCollection[i].add_link(link)
                link = self.comparatorCollection[i]

        self.outputCollection[0].add_link(self.comparatorCollection[-1])

        if len(self.outputCollection)>0:
            link = self.outputCollection[0]
            for i in range (1, len(self.outputCollection)):
                self.outputCollection[i].add_link(link)
                link = self.outputCollection[i]

        self.links_built = True

    def run(self, steps=None, verbose=False):
        for i in range(steps):
            out = self(verbose)
        return out

    def set_output(self, value):
        self.outputCollection[-1].set_value(value)

    def get_output_function(self):
        return self.outputCollection[-1]


    def set_function_name(self, collection, name, position=-1):
        if collection == "reference":
            self.referenceCollection[position].set_name(name)

        if collection == "perception":
            self.perceptionCollection[position].set_name(name)

        if collection == "comparator":
            self.comparatorCollection[position].set_name(name)

        if collection == "output":
            self.outputCollection[position].set_name(name)


    def replace_function(self, collection, function, position=-1):
        if collection == "reference":
            """
            func = self.referenceCollection[position]
            FunctionsList.getInstance().remove_function(func.get_name())
            if len(self.referenceCollection) == 0:
                position=-1
            """
            self.referenceCollection[position] = function

        if collection == "perception":
            """
            func = self.perceptionCollection[position]
            FunctionsList.getInstance().remove_function(func.get_name())
            if len(self.perceptionCollection) == 0:
                position=-1
            """
            self.perceptionCollection[position]  = function

        if collection == "comparator":
            """
            func = self.comparatorCollection[position]
            FunctionsList.getInstance().remove_function(func.get_name())
            if len(self.comparatorCollection) == 0:
                position=-1
            """
            self.comparatorCollection[position] = function

        if collection == "output":
            """
            func = self.outputCollection[position]
            FunctionsList.getInstance().remove_function(func.get_name())
            if len(self.outputCollection) == 0:
                position=-1
            """
            self.outputCollection[position] = function



    def insert_function(self, collection, function, position=-1):
        if collection == "reference":
            self.referenceCollection[position] = function

        if collection == "perception":
            self.perceptionCollection[position]  = function

        if collection == "comparator":
            self.comparatorCollection[position] = function

        if collection == "output":
            self.outputCollection[position] = function


    def summary(self, build=True):
        if build:
            if not self.links_built:
                self.build_links()

        print(self.name, type(self).__name__)
        print("----------------------------")
        print("REF:", end=" ")
        for referenceFunction in self.referenceCollection:
            referenceFunction.summary()

        print("PER:", end=" ")
        for perceptionFunction in self.perceptionCollection:
            perceptionFunction.summary()

        print("COM:", end=" ")
        for comparatorFunction in self.comparatorCollection:
            comparatorFunction.summary()

        print("OUT:", end=" ")
        for outputFunction in self.outputCollection:
            outputFunction.summary()

        print("----------------------------")


    def graph(self, layer=0, layout={'r':2,'c':1,'p':2, 'o':0}):
        graph = nx.DiGraph()

        self.set_graph_data(graph, layer=layer, layout=layout)

        return graph


    def clear_values(self):
        for referenceFunction in self.referenceCollection:
            referenceFunction.value = 0

        for comparatorFunction in self.comparatorCollection:
            comparatorFunction = 0

        for perceptionFunction in self.perceptionCollection:
            perceptionFunction = 0

        for outputFunction in self.outputCollection:
            outputFunction  = 0

    def set_graph_data_node(self, graph, layer=0):
        graph.add_node(self.name, layer=layer)

        for referenceFunction in self.referenceCollection:
            referenceFunction.set_graph_data(graph, layer+2)

        for perceptionFunction in self.perceptionCollection:
            perceptionFunction.set_graph_data(graph, layer+2)


    def set_graph_data(self, graph, layer=0, layout={'r':2,'c':1,'p':2, 'o':0}):

        for referenceFunction in self.referenceCollection:
            referenceFunction.set_graph_data(graph, layer+layout['r'])

        for comparatorFunction in self.comparatorCollection:
            comparatorFunction.set_graph_data(graph, layer+layout['c'])

        for perceptionFunction in self.perceptionCollection:
            perceptionFunction.set_graph_data(graph, layer+layout['p'])

        for outputFunction in self.outputCollection:
            outputFunction.set_graph_data(graph, layer+layout['o'])

    def get_edge_labels(self, labels):

        for func in self.referenceCollection:
            func.get_weights_labels(labels)

        for func in self.comparatorCollection:
            func.get_weights_labels(labels)

        for func in self.perceptionCollection:
            func.get_weights_labels(labels)

        for func in self.outputCollection:
            func.get_weights_labels(labels)

    def get_node_list(self, node_list):

        for func in self.referenceCollection:
            node_list[func.get_name()] = self.name

        for func in self.comparatorCollection:
            node_list[func.get_name()] = self.name

        for func in self.perceptionCollection:
            node_list[func.get_name()] = self.name

        for func in self.outputCollection:
            node_list[func.get_name()] = self.name


    def set_graph_data_node(self, graph, layer=0):
        graph.add_node(self.name, layer=layer)


    def graph_node(self, layer=0):
        graph = nx.DiGraph()

        self.set_graph_data_node(graph, layer=layer)

        return graph


    def draw_node(self, with_labels=True,  font_size=12, font_weight='bold', node_color='red',
         node_size=500, arrowsize=25, align='horizontal', file=None, figsize=(5,5), move={}):

        graph = self.graph_node()
        pos = nx.multipartite_layout(graph, subset_key="layer", align=align)
        plt.figure(figsize=figsize)
        nx.draw(graph, pos=pos, with_labels=with_labels, font_size=font_size, font_weight=font_weight,
                node_color=node_color,  node_size=node_size, arrowsize=arrowsize)



    def draw(self, with_labels=True,  font_size=12, font_weight='bold', node_color='red',
             node_size=500, arrowsize=25, align='horizontal', file=None, figsize=(5,5), move={}):

        graph = self.graph()
        pos = nx.multipartite_layout(graph, subset_key="layer", align=align)
        plt.figure(figsize=figsize)
        nx.draw(graph, pos=pos, with_labels=with_labels, font_size=font_size, font_weight=font_weight,
                node_color=node_color,  node_size=node_size, arrowsize=arrowsize)

    def get_config(self):
        config = {"type": type(self).__name__,
                    "name": self.name}

        coll_name = 'refcoll'
        collection = self.referenceCollection
        config[coll_name] = self.get_collection_config(coll_name, collection)
        coll_name = 'percoll'
        collection = self.perceptionCollection
        config[coll_name] = self.get_collection_config(coll_name, collection)
        coll_name = 'comcoll'
        collection = self.comparatorCollection
        config[coll_name] = self.get_collection_config(coll_name, collection)
        coll_name = 'outcoll'
        collection = self.outputCollection
        config[coll_name] = self.get_collection_config(coll_name, collection)

        return config

    def get_collection_config(self, coll_name, collection):
        coll = {}
        ctr=0
        for func in collection:
            coll[str(ctr)] = func.get_config()
            ctr+=1
        return coll

    def save(self, file=None, indent=4):
        jsondict = json.dumps(self.get_config(), indent=indent)
        f = open(file, "w")
        f.write(jsondict)
        f.close()

    @classmethod
    def load(cls, file):
        with open(file) as f:
            config = json.load(f)
        return cls.from_config(config)

    @classmethod
    def from_config(cls, config):
        node = PCTNode(default=False, name=config['name'])

        node.referenceCollection = []
        collection = node.referenceCollection
        coll_dict = config['refcoll']
        PCTNode.collection_from_config(collection, coll_dict)

        node.perceptionCollection = []
        collection = node.perceptionCollection
        coll_dict = config['percoll']
        PCTNode.collection_from_config(collection, coll_dict)

        node.comparatorCollection = []
        collection = node.comparatorCollection
        coll_dict = config['comcoll']
        PCTNode.collection_from_config(collection, coll_dict)

        node.outputCollection = []
        collection = node.outputCollection
        coll_dict = config['outcoll']
        PCTNode.collection_from_config(collection, coll_dict)

        node.links_built = True
        return node

    @classmethod
    def collection_from_config(node, collection, coll_dict):
        #print("collection_from_config", coll_dict)
        for fndict_label in coll_dict:
            #print("fndict_label",fndict_label)

            fndict = coll_dict[fndict_label]
            #print(fndict)
            fnname = fndict.pop('type')
            #print(fndict)
            func = eval(fnname).from_config(fndict)
            collection.append(func)


# Cell
class PCTNodeData():
    "Data collected for a PCTNode"
    def __init__(self, name="pctnodedata"):
        self.data = {
            "refcoll":{},
            "percoll":{},
            "comcoll":{},
            "outcoll":{}}


    def add_data(self, node):
        ctr = 0

        self.add_collection( node.referenceCollection, "refcoll")
        self.add_collection( node.perceptionCollection, "percoll")
        self.add_collection( node.comparatorCollection, "comcoll")
        self.add_collection( node.outputCollection, "outcoll")

    def add_collection(self, collection, collname):
        for func in collection:
            if self.data[collname].get(func.get_name()) == None:
                dlist=[]
                cdict={func.get_name():dlist}
                self.data[collname]=cdict
            else:
                dlist = self.data[collname][func.get_name()]

            dlist.append(func.get_value())