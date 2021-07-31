# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_hierarchy.ipynb (unless otherwise specified).

__all__ = ['FunctionsData', 'PCTHierarchy']

# Cell
import numpy as np
import sys
from .nodes import PCTNode
from .functions import WeightedSum
from .putils import UniqueNamer
from .putils import FunctionsList
from .functions import BaseFunction

# Cell
class FunctionsData():
    "Data collected for a set of functions"
    def __init__(self):
        self.data = {}

    def add_data(self, func):
        name = func.get_name()
        if name in self.data.keys():
            self.data[name].append(func.get_value())
        else:
            dlist=[]
            self.data[name]=dlist
            self.data[name].append(func.get_value())

    def add_reward(self, func):
        name = 'reward'
        if name in self.data.keys():
            self.data[name].append(func.get_reward())
        else:
            dlist=[]
            self.data[name]=dlist
            self.data[name].append(func.get_reward())

    def add_list(self, key, list):
        self.data[key]= list

# Cell
class PCTHierarchy():
    "A hierarchical perceptual control system, of PCTNodes."
    def __init__(self, levels=0, cols=0, pre=None, post=None, name="pcthierarchy", clear_names=True, links="single",
                 history=False, build=True, error_collector=None, **pargs):
        self.error_collector=error_collector
        self.links_built = False
        self.order=None
        self.history=history
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
        self.prepost_data = None
        if history:
            self.prepost_data = FunctionsData()

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

        for ctr in range(len(self.preCollection)):
            func = self.preCollection[ctr]
            func(verbose)
            if self.prepost_data != None:
                self.prepost_data.add_data(func)
                if ctr == 0 and hasattr(func, 'reward'):
                    self.prepost_data.add_reward(func)

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
            if self.prepost_data != None:
                self.prepost_data.add_data(func)

        output = self.get_output_function().get_value()

        if self.error_collector != None:
            self.error_collector.add_data(self)

        if verbose:
            print()

        return output

    def get_prepost_data (self):
        return self.prepost_data

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

    def get_preprocessor(self):
        return self.preCollection

    def get_postprocessor(self):
        return self.postCollection

    def run(self, steps=1, verbose=False):
        for i in range(steps):
            self.step = i
            try:
                if verbose:
                    print(f'[{i}]', end=' ')
                out = self(verbose)
            except Exception as ex:
                if ex.__str__().startswith('1000'):
                    return False
                raise ex

            if self.error_collector != None:
                if self.error_collector.is_limit_exceeded():
                    return out

        return out

    def last_step(self):
        return self.step

    def get_node(self, level, col):
        return self.hierarchy[level][col]

    def get_error_collector(self):
        return self.error_collector

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

    def get_grid(self):
        return [self.get_columns(level) for level in range(self.get_levels())]

    def get_node_positions(self, align='horizontal'):
        graph = self.graph()
        pos = nx.multipartite_layout(graph, subset_key="layer", align=align)
        return pos


    def draw(self, with_labels=True, with_edge_labels=False,  font_size=12, font_weight='bold', node_color=None,
             color_mapping={'PL':'aqua','OL':'limegreen','CL':'goldenrod', 'RL':'red', 'I':'silver', 'A':'yellow'},
             node_size=500, arrowsize=25, align='horizontal', file=None, figsize=(8,8), move={}, layout={'r':2,'c':1,'p':2, 'o':0}):
        import networkx as nx
        import matplotlib.pyplot as plt
        self.graphv = self.graph(layout=layout)
        if node_color==None:
            node_color = self.get_colors(self.graphv, color_mapping)

        pos = nx.multipartite_layout(self.graphv, subset_key="layer", align=align)

        for key in move.keys():
            pos[key][0]+=move[key][0]
            pos[key][1]+=move[key][1]

        plt.figure(figsize=figsize)
        if with_edge_labels:
            edge_labels = self.get_edge_labels()
            nx.draw_networkx_edge_labels(self.graphv, pos=pos, edge_labels=edge_labels, font_size=font_size, font_weight=font_weight,
                font_color='red')
        nx.draw(self.graphv, pos=pos, with_labels=with_labels, font_size=font_size, font_weight=font_weight,
                node_color=node_color,  node_size=node_size, arrowsize=arrowsize)

        if file != None:
            plt.title(self.name)
            plt.savefig(file)

    def get_colors(self, graph, color_mapping):
        colors=[]
        for node in graph:
            color = 'darkorchid'
            for key in color_mapping.keys():
                if node.startswith(key):
                    color = color_mapping[key]
                    break
            colors.append(color)
        return colors

    def get_edge_labels(self):
        labels={}

        for func in self.postCollection:
            func.get_weights_labels(labels)

        for func in self.preCollection:
            func.get_weights_labels(labels)

        for level in self.hierarchy:
            for node in level:
                node.get_edge_labels(labels)

        return labels

    def get_graph(self):
        return self.graphv

    def clear_graph(self):
        self.graphv.clear()

    def graph(self, layout={'r':2,'c':1,'p':2, 'o':0}):
        import networkx as nx
        graph = nx.DiGraph()

        self.set_graph_data(graph, layout=layout)

        return graph

    def set_graph_data(self, graph, layout={'r':2,'c':1,'p':2, 'o':0}):
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
                  self.hierarchy[level][col].set_graph_data(graph, layer=layer, layout=layout)
            layer+=3

    def draw_nodes(self, with_labels=True, with_edge_labels=False,  font_size=12, font_weight='bold', node_color=None,
         color_mapping={'L':'red', 'I':'silver', 'A':'yellow'},
         node_size=500, arrowsize=25, align='horizontal', file=None, figsize=(8,8), move={}):
        graph = self.graph_nodes()
        if node_color==None:
            node_color = self.get_colors(graph, color_mapping)

        pos = nx.multipartite_layout(graph, subset_key="layer", align=align)

        for key in move.keys():
            pos[key][0]+=move[key][0]
            pos[key][1]+=move[key][1]

        plt.figure(figsize=figsize)
        if with_edge_labels:
            edge_labels = self.get_edge_labels_nodes()
            nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_labels, font_size=font_size, font_weight=font_weight,
                font_color='red')
        nx.draw(graph, pos=pos, with_labels=with_labels, font_size=font_size, font_weight=font_weight,
                node_color=node_color,  node_size=node_size, arrowsize=arrowsize)

        if file != None:
            plt.title(self.name)
            plt.savefig(file)

    def get_edge_labels_nodes(self, node_list):
        labels={}

        for func in self.postCollection:
            func.get_weights_labels_nodes(labels, node_list)

        for func in self.preCollection:
            func.get_weights_labels_nodes(labels, node_list)

        for level in self.hierarchy:
            for node in level:
                node.get_edge_labels(labels)

        return labels

    def change_link_name(self, old_name, new_name):
        for func in self.postCollection:
            func.links = [new_name if i==old_name else i for i in func.links ]

        for func in self.preCollection:
            func.links = [new_name if i==old_name else i for i in func.links ]

        for level in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[level])):
                  self.hierarchy[level][col].change_link_name(old_name, new_name)

    def set_suffixes(self):

        # change names
        for key in FunctionsList.getInstance().functions.keys():
            func = FunctionsList.getInstance().get_function(key)
            if isinstance (func, BaseFunction):
                name = func.get_name()
                #print(name)
                suffix = func.get_suffix()
                func.name = name+suffix
                self.change_link_name(key, func.name)

        keys = list(FunctionsList.getInstance().functions.keys())
        for key in keys:
            func = FunctionsList.getInstance().get_function(key)
            if isinstance (func, BaseFunction):
                name = func.get_name()
                #print(key, name)
                FunctionsList.getInstance().functions[name] = FunctionsList.getInstance().functions.pop(key)


    def get_levels(self):
        return len(self.hierarchy)

    def get_columns(self, level):
        return len(self.hierarchy[level])

    def graph_nodes(self):
        graph = nx.DiGraph()

        self.set_graph_data_nodes(graph)

        return graph

    def set_graph_data_nodes(self, graph):
        layer=0
        if len(self.preCollection)>0 or len(self.postCollection)>0:
            layer=1

        node_list={}
        for level in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[level])-1, -1, -1):
                node = self.hierarchy[level][col]
                node.get_node_list(node_list)

        for func in self.preCollection:
            node_list[func.get_name()] = func.get_name()

        for func in self.postCollection:
            node_list[func.get_name()] = func.get_name()

        for func in self.postCollection:
            func.set_graph_data_node(graph, layer=0, node_list=node_list)

        for func in self.preCollection:
            func.set_graph_data_node(graph, layer=0, node_list=node_list)

        edges = []
        for level in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[level])-1, -1, -1):
                node = self.hierarchy[level][col]
                graph.add_node(node.get_name(), layer=level+layer)

                for func in node.referenceCollection:
                    for link in func.links:
                        if isinstance(link, str):
                            name=link
                        else:
                            name = link.get_name()
                        edges.append((node_list[name],node.get_name()))

                for func in node.perceptionCollection:
                    for link in func.links:
                        if isinstance(link, str):
                            name=link
                        else:
                            name = link.get_name()
                        edges.append((node_list[name],node.get_name()))

        graph.add_edges_from(edges)


    def build_links(self):
        for level in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[level])):
                  self.hierarchy[level][col].build_links()


    def clear_values(self):
        for func in self.postCollection:
            func.value = 0

        for func in self.preCollection:
            func.value = 0

        for level in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[level])):
                  self.hierarchy[level][col].clear_values()

    def error(self):
        error = 0
        for level in range(len(self.hierarchy)):
             for col in range(len(self.hierarchy[level])):
                    error += self.hierarchy[level][col].get_function("comparator").get_value()
        return error

    def insert_level(self, level):
        cols_list=[]
        self.hierarchy.insert(level, cols_list)

    def remove_level(self, level):
        self.hierarchy.pop(level)

    def summary(self, build=False):
        print(self.name, type(self).__name__)

        print("**************************")
        print("PRE:", end=" ")
        if len(self.preCollection) == 0:
            print("None")
        for func in self.preCollection:
            func.summary()


        if self.order==None:
            for level in range(len(self.hierarchy)):
                print(f'Level {level} Cols {self.get_columns(level)}')
                for col in range(len(self.hierarchy[level])):
                      self.hierarchy[level][col].summary(build=build)
        elif self.order=="Down":
            for level in range(len(self.hierarchy)-1, -1, -1):
                print(f'Level {level} Cols {self.get_columns(level)}')
                for col in range(len(self.hierarchy[level])-1, -1, -1):
                      self.hierarchy[level][col].summary(build=build)

        print("POST:", end=" ")
        if len(self.postCollection) == 0:
            print("None")
        for func in self.postCollection:
            func.summary()


        print("**************************")

    def save(self, file=None, indent=4):
        import json
        jsondict = json.dumps(self.get_config(), indent=indent)
        f = open(file, "w")
        f.write(jsondict)
        f.close()

    @classmethod
    def load(cls, file, clear=True):
        if clear:
            FunctionsList.getInstance().clear()

        with open(file) as f:
            config = json.load(f)
        return cls.from_config(config)

    def get_config(self):
        config = {"type": type(self).__name__,
                    "name": self.name}

        pre = {}
        for i in range(len(self.preCollection)):
            pre[f'pre{i}']=self.preCollection[i].get_config()
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
            post[f'post{i}']=self.postCollection[i].get_config()
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

    def replace_function(self, level=None, col=None, collection=None, function=None, position=-1):
        self.hierarchy[level][col].replace_function(collection, function, position)

    def get_function(self, level=None, col=None, collection=None, position=-1):
        return self.hierarchy[level][col].get_function(collection, position)

    def set_links(self, func_name, *link_names):
        func = FunctionsList.getInstance().get_function(func_name)
        func.clear_links()
        for link_name in link_names:
            func.add_link(FunctionsList.getInstance().get_function(link_name))

    def add_links(self, func_name, *link_names):
        for link_name in link_names:
            FunctionsList.getInstance().get_function(func_name).add_link(FunctionsList.getInstance().get_function(link_name))


    def get_history_data(self):
        history_data = self.get_prepost_data()
        #for key in history_data.data.keys():
        #    print(key)

        for level in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[level])):
                node = self.get_node(level,col)
                for key in node.history.data['refcoll'].keys():
                    #print(key)
                    history_data.add_list(key,node.history.data['refcoll'][key])
                for key in node.history.data['percoll'].keys():
                    #print(key)
                    history_data.add_list(key,node.history.data['percoll'][key])
                for key in node.history.data['comcoll'].keys():
                    #print(key)
                    history_data.add_list(key,node.history.data['comcoll'][key])
                for key in node.history.data['outcoll'].keys():
                    #print(key)
                    history_data.add_list(key,node.history.data['outcoll'][key])

        return history_data.data

    def hierarchy_plots(self, title='plot', plot_items={}, figsize=(15,4)):
        from matplotlib import style
        import matplotlib.pyplot as plt
        history = self.get_history_data()

        num_items = len(history[list(history.keys())[0]])
        x = np.linspace(0, num_items-1, num_items)
        style.use('fivethirtyeight')

        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(1,1,1)

        for key in plot_items.keys():
            ax1.plot(x, history[key], label=plot_items[key])

        plt.title(title)
        plt.legend()
        plt.show()

        return fig