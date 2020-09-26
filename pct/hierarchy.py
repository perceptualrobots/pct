# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_hierarchy.ipynb (unless otherwise specified).

__all__ = ['PCTHierarchy']

# Cell
import networkx as nx
import json
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt
import numpy as np
from .nodes import PCTNode
from .functions import *
from .putils import UniqueNamer
from .putils import FunctionsList

# Cell
class PCTHierarchy():
    "A hierarchical perceptual control system, of PCTNodes."
    def __init__(self, levels=0, cols=0, pre=None, post=None, name="pcthierarchy", clear_names=True, links="single", history=False, build=True, **pargs):
        self.links_built = False
        self.order=None
        if clear_names:
            UniqueNamer.getInstance().clear()
        self.name=UniqueNamer.getInstance().get_name(name)
        if pre==None:
            self.preCollection=[]
        else:
            self.preCollection=pre
        if post==None:
            self.postCollection=[]
        else:
            self.postCollection=post
        self.hierarchy = []
        for r in range(levels):
            col_list=[]
            for c in range(cols):
                if links == "dense":
                    if r > 0:
                        perc = WeightedSum(weights=np.ones(cols))
                    if r < levels-1:
                        ref = WeightedSum(weights=np.ones(cols))
                    if r == 0:
                        if levels > 1:
                            node = PCTNode(reference=ref, name=f'level{r}col{c}', history=history)
                        else:
                            node = PCTNode(name=f'level{r}col{c}', history=history)
                    if r > 0 and r == levels-1:
                        node = PCTNode(perception=perc, name=f'level{r}col{c}', history=history)
                    if r > 0 and r < levels-1:
                        node = PCTNode(perception=perc, reference=ref, history=history, name=f'level{r}col{c}')

                else:
                    node = PCTNode(name=f'level{r}col{c}', history=history)

                if build:
                    node.build_links()
                    self.handle_perception_links(node, r, c, links)
                    self.handle_reference_links(node, r, c, links)
                col_list.append(node)

            self.hierarchy.append(col_list)


    def __call__(self, verbose=False):

        for func in self.preCollection:
            #if verbose:
            #    print(func.get_name(), end =" ")
            func(verbose)

        if verbose:
            print()

        if self.order==None:
            for level in range(len(self.hierarchy)):
                for col in range(len(self.hierarchy[level])):
                    node  = self.hierarchy[level][col]
                    if verbose:
                        print(node.get_name(), end =" ")
                    node(verbose)
        elif self.order=="Down":
            for level in range(len(self.hierarchy)-1, -1, -1):
                for col in range(len(self.hierarchy[level])-1, -1, -1):
                    node  = self.hierarchy[level][col]
                    if verbose:
                        print(node.get_name(), end =" ")
                    node(verbose)
        else:
            for node_name in self.order:
                if verbose:
                    print(node_name, end =" ")
                FunctionsList.getInstance().get_function(node_name)(verbose)

        for func in self.postCollection:
            func(verbose)

        if verbose:
            print()

        output = self.get_output_function().get_value()

        if verbose:
            print()

        return output


    def set_order(self, order):
        self.order=order

    def get_output_function(self):
        if len(self.postCollection) > 0:
            return self.postCollection[-1]

        return self.hierarchy[-1][-1].get_output_function()

    def add_preprocessor(self, func):
        self.preCollection.append(func)

    def add_postprocessor(self, func):
        self.postCollection.append(func)

    def run(self, steps=None, verbose=False):
        for i in range(steps):
            out = self(verbose)
        return out

    def get_node(self, level, col):
        return self.hierarchy[level][col]

    def handle_perception_links(self, node, level, col, links_type):
        if level == 0 or links_type == None:
            return

        if links_type == "single":
            node.add_link("perception", self.hierarchy[level-1][col].get_function("perception"))

        if links_type == "dense":
            for column in range(len(self.hierarchy[level-1])):
                node.add_link("perception", self.hierarchy[level-1][column].get_function("perception"))

    def handle_reference_links(self, thisnode, level, col, links_type):
        if level == 0 or links_type == None:
            return

        if links_type == "single":
            thatnode = self.hierarchy[level-1][col]
            thatnode.add_link("reference", thisnode.get_function("output"))

        if links_type == "dense":
            for column in range(len(self.hierarchy[level-1])):
                thatnode = self.hierarchy[level-1][column]
                thatnode.add_link("reference", thisnode.get_function("output"))


    def get_node_positions(self, align='horizontal'):
        graph = self.graph()
        pos = nx.multipartite_layout(graph, subset_key="layer", align=align)
        return pos


    def draw(self, with_labels=True,  font_size=12, font_weight='bold', node_color='red',
             node_size=500, arrowsize=25, align='horizontal', file=None, figsize=(8,8), move={}):
        graph = self.graph()
        pos = nx.multipartite_layout(graph, subset_key="layer", align=align)

        for key in move.keys():
            pos[key][0]+=move[key][0]
            pos[key][1]+=move[key][1]

        plt.figure(figsize=figsize)
        nx.draw(graph, pos=pos, with_labels=with_labels, font_size=font_size, font_weight=font_weight,
                node_color=node_color,  node_size=node_size, arrowsize=arrowsize)
        #plt.show()

        if file != None:
            plt.title(self.name)
            plt.savefig(file)

    def graph(self):
        graph = nx.DiGraph()

        self.set_graph_data(graph)

        return graph

    def set_graph_data(self, graph):
        layer=0
        if len(self.preCollection)>0 or len(self.postCollection)>0:
            layer=1

        for func in self.postCollection:
            func.set_graph_data(graph, layer=0)

        for func in self.preCollection:
            func.set_graph_data(graph, layer=0)

        for level in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[level])-1, -1, -1):
            #for col in range(len(self.hierarchy[level])):
                  self.hierarchy[level][col].set_graph_data(graph, layer=layer)
            layer+=3



    def summary(self, build=True):
        print(self.name, type(self).__name__)

        print("**************************")
        print("PRE:", end=" ")
        if len(self.preCollection) == 0:
            print("None")
        for func in self.preCollection:
            func.summary()


        if self.order==None:
            for level in range(len(self.hierarchy)):
                print(f'Level {level}')
                for col in range(len(self.hierarchy[level])):
                      self.hierarchy[level][col].summary(build=build)
        elif self.order=="Down":
            for level in range(len(self.hierarchy)-1, -1, -1):
                print(f'Level {level}')
                for col in range(len(self.hierarchy[level])-1, -1, -1):
                      self.hierarchy[level][col].summary(build=build)

        print("POST:", end=" ")
        if len(self.postCollection) == 0:
            print("None")
        for func in self.postCollection:
            func.summary()


        print("**************************")

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

    def get_config(self):
        config = {"type": type(self).__name__,
                    "name": self.name}

        pre = {}
        for i in range(len(self.preCollection)):
            pre[f'pre{i}']=self.preCollection[0].get_config()
        config['pre']=pre


        levels = {}
        for lvl in range(len(self.hierarchy)):
            level ={'level':lvl}
            columns={}
            for col in range(len(self.hierarchy[lvl])):
                column={'col':col}
                nodeconfig = self.hierarchy[lvl][col].get_config()
                #print(nodeconfig)
                column['node']=nodeconfig
                #print(column)
                columns[f'col{col}']=column
            level['nodes']=columns
            levels[f'level{lvl}']=level
        config['levels']=levels

        post = {}
        for i in range(len(self.postCollection)):
            post[f'post{i}']=self.postCollection[0].get_config()
        config['post']=post
        return config


    @classmethod
    def from_config(cls, config):
        hpct = PCTHierarchy(name=config['name'])
        preCollection = []
        coll_dict = config['pre']
        PCTNode.collection_from_config(preCollection, coll_dict)

        postCollection = []
        coll_dict = config['post']
        PCTNode.collection_from_config(postCollection, coll_dict)

        hpct.preCollection=preCollection
        hpct.postCollection=postCollection

        hpct.hierarchy=[]
        for level_key in config['levels'].keys():
            cols = []
            for nodes_key in config['levels'][level_key]['nodes'].keys():
                node = PCTNode.from_config(config['levels'][level_key]['nodes'][nodes_key]['node'])
                cols.append(node)
            hpct.hierarchy.append(cols)


        return hpct


    def add_node(self, node, level=-1, col=-1):

        if len(self.hierarchy)==0:
            self.hierarchy.append([])

        if level<0 and col<0:
            self.hierarchy[0].append(node)
        else:
            levels = len(self.hierarchy)
            if level == levels:
                self.hierarchy.append([])
            self.hierarchy[level].insert(col, node)

    def insert_function(self, level=None, col=None, collection=None, function=None, position=-1):
        self.hierarchy[level][col].insert_function(collection, function, position)

    def get_function(self, level=None, col=None, collection=None, position=-1):
        return self.hierarchy[level][col].get_function(collection, position)

    def set_links(self, func_name, *link_names):
        for link_name in link_names:
            FunctionsList.getInstance().get_function(func_name).set_link(FunctionsList.getInstance().get_function(link_name))

    def add_links(self, func_name, *link_names):
        for link_name in link_names:
            FunctionsList.getInstance().get_function(func_name).add_link(FunctionsList.getInstance().get_function(link_name))