# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_nodes.ipynb (unless otherwise specified).

__all__ = ['PCTNode', 'PCTNodeData']

# Cell
from .functions import *

# Cell
class PCTNode():
    "A single PCT controller."
    def __init__(self, reference=None, perception=None, comparator=None, output=None, name="pctnode", history=False, **pargs):
        self.links_built = False
        self.history = None
        if history:
            self.history = PCTNodeData()
        self.name = UniqueNamer.getInstance().get_name(name)
        if perception==None:
            perception =  Variable(0)
        self.perceptionCollection = [perception]

        if reference==None:
            reference = Constant(1)
        self.referenceCollection = [reference]

        if comparator==None:
            comparator = Subtract()
        self.comparatorCollection = [comparator]

        if output==None:
            output = Proportional(10)

        self.outputCollection = [output]

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


    def summary(self):
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

    @classmethod
    def from_config(cls, config):
        node = PCTNode(name=config['name'])

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

        node.build_links()
        return node

    @classmethod
    def collection_from_config(node, collection, coll_dict):
        print("collection_from_config", coll_dict)
        for fndict_label in coll_dict:
            print("fndict_label",fndict_label)

            fndict = coll_dict[fndict_label]
            #print(fndict)
            fnname = fndict.pop('type')
            print(fndict)
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