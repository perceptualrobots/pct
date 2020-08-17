# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_hierarchy.ipynb (unless otherwise specified).

__all__ = ['PCTHierarchy']

# Cell
import numpy as np
from .nodes import PCTNode
from .functions import *

# Cell
class PCTHierarchy():
    "A hierarchical perceptual control system, of PCTNodes."
    def __init__(self, rows=0, cols=0, pre=[], post=[], name="pcthierarchy", links="single", history=False, **pargs):
        self.links_built = False
        UniqueNamer.getInstance().clear()
        self.name=UniqueNamer.getInstance().get_name(name)
        self.preCollection=pre
        self.postCollection=post
        self.hierarchy = []
        for r in range(rows):
            col_list=[]
            for c in range(cols):
                if links == "dense":
                    if r > 0:
                        perc = WeightedSum(weights=np.ones(cols))
                    if r < rows-1:
                        ref = WeightedSum(weights=np.ones(cols))
                    if r == 0:
                        node = PCTNode(reference=ref, name=f'row{r}col{c}', history=history)
                    if r > 0 and r == rows-1:
                        node = PCTNode(perception=perc, name=f'row{r}col{c}', history=history)
                    if r > 0 and r < rows-1:
                        node = PCTNode(perception=perc, reference=ref, history=history, name=f'row{r}col{c}')

                else:
                    node = PCTNode(name=f'row{r}col{c}', history=history)
                    node.build_links()

                self.handle_perception_links(node, r, c, links)
                self.handle_reference_links(node, r, c, links)
                col_list.append(node)

            self.hierarchy.append(col_list)


    def __call__(self, verbose=False):

        for func in self.preCollection:
            if verbose:
                print(func.get_name(), end =" ")
            func(verbose)

        if verbose:
            print()

        for row in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[row])):
                node  = self.hierarchy[row][col]
                if verbose:
                    print(node.get_name(), end =" ")
                node(verbose)

        for func in self.postCollection:
            if verbose:
                print(func.get_name(), end =" ")
            func(verbose)

        if verbose:
            print()

        output = self.postCollection[-1].get_value()

        if verbose:
            print()

        return output

    def run(self, steps=None, verbose=False):
        for i in range(steps):
            out = self(verbose)
        return out

    def get_node(self, row, col):
        return self.hierarchy[row][col]

    def handle_perception_links(self, node, row, col, links_type):
        if row == 0 or links_type == None:
            return

        if links_type == "single":
            node.add_link("perception", self.hierarchy[row-1][col].get_function("perception"))

        if links_type == "dense":
            for column in range(len(self.hierarchy[row-1])):
                node.add_link("perception", self.hierarchy[row-1][column].get_function("perception"))

    def handle_reference_links(self, thisnode, row, col, links_type):
        if row == 0 or links_type == None:
            return

        if links_type == "single":
            thatnode = self.hierarchy[row-1][col]
            thatnode.add_link("reference", thisnode.get_function("output"))

        if links_type == "dense":
            for column in range(len(self.hierarchy[row-1])):
                thatnode = self.hierarchy[row-1][column]
                thatnode.add_link("reference", thisnode.get_function("output"))


    def get_config(self):
        config = {"type": type(self).__name__,
                    "name": self.name}

        pre = {}
        for i in range(len(self.preCollection)):
            pre[f'pre{i}']=self.preCollection[0].get_config()
        config['pre']=pre


        levels = {}
        for row in range(len(self.hierarchy)):
            level ={'level':row}
            columns={}
            for col in range(len(self.hierarchy[row])):
                column={'col':col}
                nodeconfig = self.hierarchy[row][col].get_config()
                #print(nodeconfig)
                column['node']=nodeconfig
                #print(column)
                columns[f'col{col}']=column
            level['nodes']=columns
            levels[f'level{row}']=level
        config['levels']=levels

        post = {}
        for i in range(len(self.postCollection)):
            post[f'post{i}']=self.postCollection[0].get_config()
        config['post']=post
        return config


    @classmethod
    def from_config(cls, config):

        preCollection = []
        coll_dict = config['pre']
        PCTNode.collection_from_config(preCollection, coll_dict)

        postCollection = []
        coll_dict = config['post']
        PCTNode.collection_from_config(postCollection, coll_dict)

        hpct = PCTHierarchy(pre=preCollection, post=postCollection, name=config['name'])

        hpct.hierarchy=[]
        for level_key in config['levels'].keys():
            cols = []
            for nodes_key in config['levels'][level_key]['nodes'].keys():
                print(nodes_key)
                print(config['levels'][level_key]['nodes'][nodes_key]['node'])
                node = PCTNode.from_config(config['levels'][level_key]['nodes'][nodes_key]['node'])
                cols.append(node)
            hpct.hierarchy.append(cols)


        """
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
        """
        return hpct

