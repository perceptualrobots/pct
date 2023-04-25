# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_hierarchy.ipynb.

# %% auto 0
__all__ = ['FunctionsData', 'PCTHierarchy']

# %% ../nbs/04_hierarchy.ipynb 4
#import numpy as np
import sys
import uuid
from .nodes import PCTNode
from .functions import WeightedSum
from .putils import UniqueNamer, FunctionsList, list_of_ones
from .functions import BaseFunction
from .environments import EnvironmentFactory
from .errors import BaseErrorCollector

# %% ../nbs/04_hierarchy.ipynb 6
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

# %% ../nbs/04_hierarchy.ipynb 7
class PCTHierarchy():
    "A hierarchical perceptual control system, of PCTNodes."
    def __init__(self, levels=0, cols=0, pre=None, post=None, name="pcthierarchy", clear_names=True, links="single", 
                 history=False, build=True, error_collector=None, namespace=None, **pargs):
        if namespace ==None:
            namespace = uuid.uuid1()
        self.namespace=namespace

        self.error_collector=error_collector
        self.links_built = False
        self.order=None
        self.history=history
        if clear_names:
            UniqueNamer.getInstance().clear(namespace=namespace)
        self.name=UniqueNamer.getInstance().get_name(namespace=namespace, name=name)
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
                        perc = WeightedSum(weights=list_of_ones(cols), namespace=namespace)
                    if r < levels-1:
                        ref = WeightedSum(weights=list_of_ones(cols), namespace=namespace)
                    if r == 0:
                        if levels > 1:
                            node = PCTNode(reference=ref, name=f'level{r}col{c}', history=history, namespace=namespace)      
                        else:
                            node = PCTNode(name=f'level{r}col{c}', history=history, namespace=namespace)                              
                    if r > 0 and r == levels-1:                        
                        node = PCTNode(perception=perc, name=f'level{r}col{c}', history=history, namespace=namespace)
                    if r > 0 and r < levels-1:
                        node = PCTNode(perception=perc, reference=ref, history=history, name=f'level{r}col{c}', namespace=namespace)

                else:
                    node = PCTNode(name=f'level{r}col{c}', history=history, namespace=namespace)
                
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
                FunctionsList.getInstance().get_function(self.namespace, node_name)(verbose)
        
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
    

    def set_name(self, name):
        self.name=name    
    
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
                    self.error_collector.override_value()
                    if verbose:
                        print(f'Current score={self.error_collector.error()}')                    
                    return False
                elif ex.__str__().startswith('1001'):
                    return False

                raise ex

            if verbose:
                print(f'Current score={self.error_collector.error()}')
            
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

    def set_error_collector(self, error_collector):
        self.error_collector = error_collector

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
 
            
    def draw(self, with_labels=True, with_edge_labels=False,  font_size=12, font_weight='bold', font_color='black', 
             color_mapping={'PL':'aqua','OL':'limegreen','CL':'goldenrod', 'RL':'red', 'I':'silver', 'A':'yellow'},
             node_size=500, arrowsize=25, align='horizontal', file=None, figsize=(8,8), move={}, 
             node_color=None, layout={'r':2,'c':1,'p':2, 'o':0}, funcdata=False):
        import networkx as nx
        import matplotlib.pyplot as plt
        self.graphv = self.graph(layout=layout, funcdata=funcdata)
        if node_color==None:
            node_color = self.get_colors(self.graphv, color_mapping)

        pos = nx.multipartite_layout(self.graphv, subset_key="layer", align=align)
        
        for key in move.keys():            
            pos[key][0]+=move[key][0]
            pos[key][1]+=move[key][1]
        
        plt.figure(figsize=figsize) 
        if with_edge_labels:
            edge_labels = self.get_edge_labels_wrapper(funcdata)
            nx.draw_networkx_edge_labels(self.graphv, pos=pos, edge_labels=edge_labels, font_size=font_size, 
                font_weight=font_weight, font_color='red', horizontalalignment='left')
            
        nx.draw(self.graphv, pos=pos, with_labels=with_labels, font_size=font_size, font_weight=font_weight, 
                font_color=font_color, node_color=node_color,  node_size=node_size, arrowsize=arrowsize)
        
        if file != None:
            plt.title(self.name)
            plt.tight_layout()
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
            
    def reset(self):
        for func in self.preCollection:
            func.set_value(0)               

        for func in self.postCollection:
            func.set_value(0)

        for level in self.hierarchy:
            for node in level:
                node.reset()

        
    def reset_checklinks(self, val=True):
        for func in self.postCollection:
            func.reset_checklinks(val)
                    
        for func in self.preCollection:
            func.reset_checklinks(val)
            
        for level in self.hierarchy:
            for node in level:
                node.reset_checklinks(val)
                
    def get_edge_labels_wrapper(self, funcdata=False):
        if funcdata:
            return self.get_edge_labels_funcdata()
        else:
            return self.get_edge_labels()

        
    def get_edge_labels_funcdata(self):
        labels={}
       
        for func in self.postCollection:
            func.get_weights_labels_funcdata(labels)
                    
        for func in self.preCollection:
            func.get_weights_labels_funcdata(labels)
            
        for level in self.hierarchy:
            for node in level:
                node.get_edge_labels_funcdata(labels)
                
        return labels
        
        
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

    def change_namespace(self):        
        namespace = uuid.uuid1()
        self.namespace=namespace       
        self.name=UniqueNamer.getInstance().get_name(namespace=namespace, name=self.name)
        
        for func in self.postCollection:
            func.change_namespace(namespace)
                    
        for func in self.preCollection:
            func.change_namespace(namespace)
            
        for level in self.hierarchy:
            for node in level:
                node.change_namespace(namespace)
                
    
    def get_graph(self):
        return self.graphv
    
    def clear_graph(self):
        self.graphv.clear()

    def graph(self, layout={'r':2,'c':1,'p':2, 'o':0}, funcdata=False):
        import networkx as nx
        graph = nx.DiGraph()
        
        if funcdata:
            self.set_graph_data_funcdata(graph, layout=layout)
        else:
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

            
            
    def set_graph_data_funcdata(self, graph, layout={'r':2,'c':1,'p':2, 'o':0}):
        layer=0
        if len(self.preCollection)>0 or len(self.postCollection)>0:
            layer=1
            
        for func in self.postCollection:
            func.set_graph_data_funcdata(graph, layer=0)  

        for func in self.preCollection:
            func.set_graph_data_funcdata(graph, layer=0)   
                    
        for level in range(len(self.hierarchy)):
            for col in range(len(self.hierarchy[level])-1, -1, -1):
            #for col in range(len(self.hierarchy[level])):
                  self.hierarchy[level][col].set_graph_data_funcdata(graph, layer=layer, layout=layout)
            layer+=3
            
            
            
#     def draw_nodes(self, with_labels=True, with_edge_labels=False,  font_size=12, font_weight='bold', node_color=None,  
#          color_mapping={'L':'red', 'I':'silver', 'A':'yellow'},
#          node_size=500, arrowsize=25, align='horizontal', file=None, figsize=(8,8), move={}):
#         graph = self.graph_nodes()
#         if node_color==None:
#             node_color = self.get_colors(graph, color_mapping)

#         pos = nx.multipartite_layout(graph, subset_key="layer", align=align)

#         for key in move.keys():            
#             pos[key][0]+=move[key][0]
#             pos[key][1]+=move[key][1]

#         plt.figure(figsize=figsize) 
#         if with_edge_labels:
#             edge_labels = self.get_edge_labels_nodes()
#             nx.draw_networkx_edge_labels(graph, pos=pos, edge_labels=edge_labels, font_size=font_size, font_weight=font_weight, 
#                 font_color='red')
#         nx.draw(graph, pos=pos, with_labels=with_labels, font_size=font_size, font_weight=font_weight, 
#                 node_color=node_color,  node_size=node_size, arrowsize=arrowsize)

#         if file != None:
#             plt.title(self.name)
#             plt.savefig(file)

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
        functionsList = FunctionsList.getInstance()
        # change names
        for key in functionsList.functions[self.namespace].keys():
            func = functionsList.get_function(self.namespace, key)
            if isinstance (func, BaseFunction):
                name = func.get_name()
                #print(name)
                suffix = func.get_suffix()
                if len(suffix)>0:
                    func.name = name+suffix
                    self.change_link_name(key, func.name)

        keys = list(functionsList.functions[self.namespace].keys())
        for key in keys:
            func = functionsList.get_function(self.namespace,key)
            if isinstance (func, BaseFunction):
                name = func.get_name()
                #print(key, name)
                if key != name:
                    popped = functionsList.functions[self.namespace].pop(key)
                    functionsList.functions[self.namespace][name] = popped


    def get_levels(self):
        return len(self.hierarchy)
    
    def get_columns(self, level):
        return len(self.hierarchy[level])

#     def graph_nodes(self):
#         graph = nx.DiGraph()

#         self.set_graph_data_nodes(graph)

#         return graph

#     def set_graph_data_nodes(self, graph):
#         layer=0
#         if len(self.preCollection)>0 or len(self.postCollection)>0:
#             layer=1

#         node_list={}
#         for level in range(len(self.hierarchy)):
#             for col in range(len(self.hierarchy[level])-1, -1, -1):
#                 node = self.hierarchy[level][col]
#                 node.get_node_list(node_list)

#         for func in self.preCollection:
#             node_list[func.get_name()] = func.get_name()

#         for func in self.postCollection:
#             node_list[func.get_name()] = func.get_name()

#         for func in self.postCollection:
#             func.set_graph_data_node(graph, layer=0, node_list=node_list)

#         for func in self.preCollection:
#             func.set_graph_data_node(graph, layer=0, node_list=node_list)

#         edges = []
#         for level in range(len(self.hierarchy)):
#             for col in range(len(self.hierarchy[level])-1, -1, -1):
#                 node = self.hierarchy[level][col]
#                 graph.add_node(node.get_name(), layer=level+layer)

#                 for func in node.referenceCollection:
#                     for link in func.links:
#                         if isinstance(link, str):
#                             name=link
#                         else:
#                             name = link.get_name()                            
#                         edges.append((node_list[name],node.get_name()))

#                 for func in node.perceptionCollection:
#                     for link in func.links:
#                         if isinstance(link, str):
#                             name=link
#                         else:
#                             name = link.get_name()                            
#                         edges.append((node_list[name],node.get_name()))
                        
#         graph.add_edges_from(edges)

    
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
        
    def remove_level(self, lvl):
        level = self.hierarchy.pop(lvl)
        for node in level:
            node.delete_contents()
            del node
        del level


    def remove_nodes(self, level, num_nodes):        
        for _ in range(num_nodes):
            del self.hierarchy[level][-1]

    def summary(self, build=False, extra=False):
        print("**************************")
        print(self.name, type(self).__name__, self.get_grid(), self.namespace)                
        print("--------------------------")
        print("PRE:", end=" ")
        if len(self.preCollection) == 0:
            print("None")
        for func in self.preCollection:
            func.summary(extra=extra)   
        
            
        if self.order==None:
            for level in range(len(self.hierarchy)):
                print(f'Level {level} Cols {self.get_columns(level)}')
                for col in range(len(self.hierarchy[level])):
                      self.hierarchy[level][col].summary(build=build, extra=extra)
        elif self.order=="Down":
            for level in range(len(self.hierarchy)-1, -1, -1):
                print(f'Level {level} Cols {self.get_columns(level)}')
                for col in range(len(self.hierarchy[level])-1, -1, -1):
                      self.hierarchy[level][col].summary(build=build, extra=extra)
                                             
        print("POST:", end=" ")
        if len(self.postCollection) == 0:
            print("None")
        for func in self.postCollection:
            func.summary(extra=extra)   


        print("**************************")
            
    def save(self, file=None, indent=4):
        import json
        jsondict = json.dumps(self.get_config(), indent=indent)
        f = open(file, "w")
        f.write(jsondict)
        f.close()
        
    @classmethod
    def load(cls, file, clear=True, namespace=None):
        if clear:
            FunctionsList.getInstance().clear()

        with open(file) as f:
            config = json.load(f)
        return cls.from_config(config, namespace=namespace)
                   
    def get_config(self, zero=1):
        config = {"type": type(self).__name__,
                    "name": self.name}        
        
        pre = {}
        for i in range(len(self.preCollection)):
            pre[f'pre{i}']=self.preCollection[i].get_config(zero=zero)
        config['pre']=pre

        
        levels = {}
        for lvl in range(len(self.hierarchy)):
            level ={'level':lvl}
            columns={}
            for col in range(len(self.hierarchy[lvl])):
                column={'col':col}
                nodeconfig = self.hierarchy[lvl][col].get_config(zero=zero)
                #print(nodeconfig)
                column['node']=nodeconfig
                #print(column)
                columns[f'col{col}']=column
            level['nodes']=columns
            levels[f'level{lvl}']=level
        config['levels']=levels
        
        post = {}
        for i in range(len(self.postCollection)):
            post[f'post{i}']=self.postCollection[i].get_config(zero=zero)
        config['post']=post
        return config       

    
    @classmethod
    def from_config(cls, config, namespace=None):
        hpct = PCTHierarchy(name=config['name'], namespace=namespace)
        namespace = hpct.namespace
        preCollection = []        
        coll_dict = config['pre']
        PCTNode.collection_from_config(preCollection, coll_dict, namespace=namespace)
        
        postCollection = []        
        coll_dict = config['post']
        PCTNode.collection_from_config(postCollection, coll_dict, namespace=namespace)
     
        hpct.preCollection=preCollection
        hpct.postCollection=postCollection
                
        hpct.hierarchy=[]
        for level_key in config['levels'].keys():
            cols = []
            for nodes_key in config['levels'][level_key]['nodes'].keys():
                node = PCTNode.from_config(config['levels'][level_key]['nodes'][nodes_key]['node'], namespace=namespace, reference=True, comparator=True, perception=True, output=True)
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
        func = FunctionsList.getInstance().get_function(self.namespace, func_name)
        func.clear_links()
        for link_name in link_names:
            func.add_link(FunctionsList.getInstance().get_function(self.namespace, link_name))
            
    def add_links(self, func_name, *link_names):
        for link_name in link_names:
            FunctionsList.getInstance().get_function(self.namespace, func_name).add_link(FunctionsList.getInstance().get_function(self.namespace, link_name))
            
            
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
    
    def hierarchy_plots(self, title='plot', plot_items={}, figsize=(15,4), file=None):
        from matplotlib import style
        import matplotlib.pyplot as plt
        history = self.get_history_data()

        num_items = len(history[list(history.keys())[0]])
        #x = np.linspace(0, num_items-1, num_items)
        x =  [i for i in range(num_items)]
        style.use('fivethirtyeight')

        fig = plt.figure(figsize=figsize)
        ax1 = fig.add_subplot(1,1,1)

        for key in plot_items.keys():    
            ax1.plot(x, history[key], label=plot_items[key])

        if file != None:
            plt.title(title)
            plt.legend()
            plt.savefig(file)
            
        # plt.show()

        return fig
    
    def get_parameters_list(self):

        pre = []
        post = []

        for func in self.preCollection:
            pre.append(func.get_parameters_list())
        
        for func in self.postCollection:
            post.append(func.get_parameters_list())
                    
        lowest = [pre, post]

        hpct=[lowest]
        
        for level in self.hierarchy:
            level_list=[]
            for node in level:
                level_list.append(node.get_parameters_list())
            hpct.append(level_list)
                
        return hpct
    
    @classmethod
    def from_config_with_environment(cls, config, seed=None, history=False, suffixes=False):
        "Create an individual from a provided configuration."
        hpct = PCTHierarchy(history=history)
        namespace = hpct.namespace
        #print(namespace)
        preCollection = []        
        coll_dict = config['pre']
        env_dict = coll_dict.pop('pre0')

        env = EnvironmentFactory.createEnvironmentWithNamespace(env_dict['type'], namespace=namespace, seed=seed)
        for key, link in env_dict['links'].items():
            env.add_link(link)
        preCollection.append(env)
        PCTNode.collection_from_config(preCollection, coll_dict, namespace=namespace)
        
        hpct.preCollection=preCollection
                
        hpct.hierarchy=[]

        # do in order of perceptions from bottom 
        # then from top references, comparator and output

        for level_key in config['levels']:
            cols = []
            for nodes_key in config['levels'][level_key]['nodes']:
                node = PCTNode.from_config(config['levels'][level_key]['nodes'][nodes_key]['node'], namespace=namespace, perception=True, history=history)
                cols.append(node)
            hpct.hierarchy.append(cols)

        for level_key, level_value in dict(reversed(list(config['levels'].items()))).items():
            cols = []
            for nodes_key, nodes_value in dict(reversed(list(level_value['nodes'].items()))).items():
                node = hpct.get_node(level_value['level'], nodes_value['col'])
                PCTNode.from_config(config=nodes_value['node'], namespace=namespace, reference=True, comparator=True,  output=True, node=node, history=history)
                
        postCollection = []        
        coll_dict = config['post']
        PCTNode.collection_from_config(postCollection, coll_dict, namespace=namespace)
        hpct.postCollection=postCollection

        if suffixes:
            hpct.set_suffixes()
        return hpct
    
    @classmethod
    def run_from_config(cls, config, min, render=False,  error_collector_type=None, error_response_type=None, 
        error_properties=None, error_limit=100, steps=500, hpct_verbose=False, early_termination=False, 
        seed=None, draw_file=None, move=None, with_edge_labels=True, font_size=6, node_size=100, plots=None,
        history=False, suffixes=False, plots_figsize=(15,4), plots_dir=None, flip_error_response=False):
        "Run an individual from a provided configuration."
        ind = cls.from_config_with_environment(config, seed=seed, history=history, suffixes=suffixes)
        env = ind.get_preprocessor()[0]
        env.set_render(render)
        env.early_termination = early_termination
        env.reset(full=False, seed=seed)
        if error_collector_type is not None:
            error_collector = BaseErrorCollector.collector(error_response_type, error_collector_type, error_limit, min, properties=error_properties, flip_error_response=flip_error_response)
            ind.set_error_collector(error_collector)
        if hpct_verbose:
            ind.summary()
            print(ind.formatted_config())
        ind.run(steps, hpct_verbose)
        env.close()
        
        # draw network file
        move = {} if move == None else move
        if draw_file is not None:
            ind.draw(file=draw_file, move=move, with_edge_labels=with_edge_labels, font_size=font_size, node_size=node_size)
            print(draw_file)
        
        if history:
            for plot in plots:
                fig = ind.hierarchy_plots(title=plot['title'], plot_items=plot['plot_items'], figsize=plots_figsize, file=plots_dir+ sep +plot['title']+'.png')

        score=ind.get_error_collector().error()
        
        return ind, score    
