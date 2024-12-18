# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/19_pct_examples.ipynb.

# %% auto 0
__all__ = ['PCTExamples']

# %% ../nbs/19_pct_examples.ipynb 3
import json
import matplotlib.pyplot as plt
import networkx as nx



# %% ../nbs/19_pct_examples.ipynb 4
from .hierarchy import PCTHierarchy

# %% ../nbs/19_pct_examples.ipynb 6
class PCTExamples:
    """
    PCTExamples class provides methods to load a PCT hierarchy from a configuration file, 
    summarize the hierarchy, get the configuration, draw the hierarchy, run the hierarchy 
    for a specified number of steps, and close the environment.
    Attributes:
        hierarchy (PCTHierarchy): The loaded PCT hierarchy.
        env (Environment): The environment associated with the PCT hierarchy.
    """

    def __init__(self, config_file, min=True, early_termination=False, history=False):
        """
        Initializes the PCTExamples instance by loading the hierarchy from the given configuration file.
        """
        self.hierarchy, self.env = PCTHierarchy.load_from_file(config_file, min=min, early_termination=early_termination, history=history)
        self.history_data = None
        self.history = history

    def summary(self):
        """
        Prints a summary of the hierarchy.
        """
        self.hierarchy.summary()

    def get_config(self):
        """
        Returns the configuration of the hierarchy.
        """
        return self.hierarchy.get_config()

    def draw(self, with_labels=True, with_edge_labels=False, font_size=12, font_weight='bold', font_color='black', 
                       color_mapping={'PL':'aqua','OL':'limegreen','CL':'goldenrod', 'RL':'red', 'I':'silver', 'A':'yellow'},
                       node_size=500, arrowsize=25, align='horizontal', file=None, figsize=(8,8), move={}, draw_fig=True,
                       node_color=None, layout={'r':2,'c':1,'p':2, 'o':0}, funcdata=False, interactive_mode=False, experiment=None):
        """
        Draws the hierarchy with the specified parameters and returns the figure.
        """
        fig = self.hierarchy.draw(with_labels, with_edge_labels, font_size, font_weight, font_color, color_mapping, node_size, 
                            arrowsize, align, file, figsize, move, draw_fig, node_color, layout, funcdata, interactive_mode, experiment)
        
        return fig

    def run(self, steps=1, verbose=False, render=False):
        """
        Runs the hierarchy for the specified number of steps and returns the result.
        """
        self.hierarchy.get_preprocessor()[0].set_render(render)
        return self.hierarchy.run(steps, verbose)
    
    def close(self):
        """
        Closes the environment.
        """
        self.env.close()

    def get_history_keys(self):
        """
        Returns the keys of the history data of the hierarchy.
        """
        if self.history :
            if self.history_data is None:
                self.history_data = self.hierarchy.get_history_data()
            return list(self.history_data.keys())
        else:
            print("History is not enabled")

        return None

    def set_history_data(self):
        """
        Sets the history data of the hierarchy.
        """
        if self.history :

            if self.history_data is None:
                self.history_data = self.hierarchy.get_history_data()

            return self.history_data
        else:
            print("History is not enabled")

        return None

                
    
    def plot_history(self, plots=None, title_prefix='', plots_dir=None, plots_figsize=(12, 6), history_data=None):
        """
        Plots the history of the hierarchy.
        """
        print(plots)
        plots = self.hierarchy.get_plots_config(plots, title_prefix)
        print(plots)

        from os import sep
        for plot in plots:
            print(plot)
            plotfile=None
            if plots_dir:
                plotfile = plots_dir + sep + plot['title'] + '-' + str(self.hierarchy.get_namespace()) + '.png'
            fig = self.hierarchy.hierarchy_plots(title=plot['title'], plot_items=plot['plot_items'], figsize=plots_figsize, file=plotfile, history=history_data)
            # import matplotlib.pyplot as plt
            # plt.close(fig)  # Close the figure here
    
        return fig
    
    def plot_single(self, plot=None, title_prefix='', plots_dir=None, plots_figsize=(12, 6), history_data=None):
        """
        Plot one item of the history of the hierarchy.
        """

        from os import sep

        plotfile=None
        if plots_dir:
            plotfile = plots_dir + sep + plot['title'] + '-' + str(self.hierarchy.get_namespace()) + '.png'
        fig = self.hierarchy.hierarchy_plots(title=plot['title'], plot_items=plot['plot_items'], figsize=plots_figsize, file=plotfile, history=history_data)
            # import matplotlib.pyplot as plt
            # plt.close(fig)  # Close the figure here
    
        return fig
    

    
