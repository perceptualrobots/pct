"""
PCT Hierarchy Visualization from Configuration Files

This module provides functionality to generate network diagrams from PCT hierarchy 
configuration files with reproducible layouts.

For complete layout reproducibility across script executions, set the PYTHONHASHSEED 
environment variable before running Python:
    Windows PowerShell: $env:PYTHONHASHSEED=42; python draw_from_file.py ...
    Command Prompt: set PYTHONHASHSEED=42 && python draw_from_file.py ...
    Unix/Linux: PYTHONHASHSEED=42 python draw_from_file.py ...
"""
import argparse
from os import sep, makedirs
from pct.hierarchy import PCTHierarchy
import numpy as np
import random


def drawit(filename=None, outdir=None, funcdata=False, font_size=8, node_size=300, move={}, suffixes=False, layout_seed=42):
    import numpy as np
    import random
    import networkx as nx
    import os
    
    # Note: PYTHONHASHSEED should be set at environment level for full reproducibility
    # This affects dictionary ordering across script executions
    # Already set in environment: PYTHONHASHSEED=42
    
    # Set multiple random seeds for consistency
    np.random.seed(layout_seed)
    random.seed(layout_seed)
    
    # Set NetworkX random state
    try:
        nx.random.seed(layout_seed)
    except AttributeError:
        pass  # Older NetworkX versions may not have this
    
    if filename is None or outdir is None:
        raise ValueError("filename and outdir must be provided")
        
    # Find the last separator (either \ or /) to handle both Windows and Unix paths
    backslash_pos = filename.rfind('\\')
    slash_pos = filename.rfind('/')
    lastsepIndex = max(backslash_pos, slash_pos)
    input_filename = filename[lastsepIndex+1:]
    draw_file = outdir + sep + 'draw-' + input_filename.replace('.properties', '.png')

    hpct, _ , _ = PCTHierarchy.load_from_file(filename)
    hpct.validate_links()
    if suffixes:
        hpct.set_suffixes()
    # hpct.summary()

    # Set seed again right before drawing to ensure consistent layout
    np.random.seed(layout_seed)
    random.seed(layout_seed)
    hpct.draw(file=draw_file, move=move, with_edge_labels=True, font_size=font_size, node_size=node_size, funcdata=funcdata, layout_seed=layout_seed)
    print('Image saved to '+draw_file)

    if hpct.consolidate():
        move={}
        draw_file = outdir + sep + 'draw-' + input_filename.replace('.properties', '_consolidate.png')
        # Set seed again for the consolidated drawing
        np.random.seed(layout_seed)
        random.seed(layout_seed)
        hpct.draw(file=draw_file, move=move, with_edge_labels=True, font_size=font_size, node_size=node_size, funcdata=funcdata, layout_seed=layout_seed)
        print('Image saved to '+draw_file)


"""
Examples:

python -m pct.applications.draw_from_file -f "C:/Users/ryoung/Versioning/python/nbdev/pct/nbs/testfiles/MountainCar/MountainCar-cdf7cc1497ad143c0b04a3d9e72ab783.properties" -o "/tmp" 
python -m pct.applications.draw_from_file -s -f "C:/Users/ryoung/Versioning/python/nbdev/pct/nbs/testfiles/MountainCar/MountainCar-cdf7cc1497ad143c0b04a3d9e72ab783.properties" -o "/tmp" 

$env:PYTHONHASHSEED=1; python -m pct.applications.draw_from_file -l  1 -s -f "C:/Users/ryoung/Versioning/python/nbdev/pct/nbs/testfiles/MountainCar/MountainCar-cdf7cc1497ad143c0b04a3d9e72ab783.properties" -o "/tmp" -m "{'IV':[0, 0.05],'IP':[-0.6, 0.3],  'OL0C0sm':[-0.28, -0.2],'OL0C1sm':[0.28, -0.2], 'OL1C0sm':[0,-0.1], 'MountainCarContinuousV0':[-.7,-0.5], 'Action1ws':[-0.4,-0.3]}"

$env:PYTHONHASHSEED=1; python -m pct.applications.draw_from_file -s -f "C:/Users/ryoung/Versioning/python/nbdev/pct/nbs/testfiles/MountainCar/MountainCar-cdf7cc1497ad143c0b04a3d9e72ab783.properties" -o "/tmp" -m "{'IV':[0, 0.05],'IP':[-0.6, 0.3],  'OL0C0sm':[-0.28, -0.2],'OL0C1sm':[0.28, -0.2], 'OL1C0sm':[0,-0.1], 'MountainCarContinuousV0':[-.7,-0.5], 'Action1ws':[-0.4,-0.3]}"

$env:PYTHONHASHSEED=1; python -m pct.applications.draw_from_file -s -f "C:/Users/ryoung/Versioning/python/nbdev/pct/nbs/testfiles/MountainCar/MountainCar-cdf7cc1497ad143c0b04a3d9e72ab783.properties" -o "/tmp" -m "{'IV':[-0.2, 0.1],'IP':[-1.2, 0.3],  'OL0C0sm':[-0.28, -0.2],'OL0C1sm':[0.28, -0.2], 'OL1C0sm':[0,-0.1], 'MountainCarContinuousV0':[-.7,-0.5], 'Action1ws':[0.4,-0.3], 'CL1C0':[0,0], 'OL1C0sm':[0,0], 'RL0C0sm':[0,0], 'PL0C0sm':[-0.5,0], 'CL0C0':[-0.275,0], 'RL0C1sm':[0,0], 'PL0C1sm':[0.55,0], 'CL0C1':[0.275, 0] }"

          


"""

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help="file name")
    parser.add_argument('-o', '--outdir', type=str, help="directory to save drawing")
    parser.add_argument('-t', '--font_size',  type=int, help="font size", default="6")
    parser.add_argument('-n', '--node_size',  type=int, help="node size", default="200")
    parser.add_argument("-m", "--move", type=str, help="node positioning")
    parser.add_argument("-d", "--funcdata", help="include function labels", action="store_true")
    parser.add_argument("-s", "--suffixes", help="add function suffixes", action="store_true")
    parser.add_argument("-l", "--layout_seed", type=int, help="seed for consistent layout", default=42)

    args = parser.parse_args()

    if args.move is None:
        move = {}
    else:
        move = eval(args.move)

    drawit(filename=args.file, outdir=args.outdir, funcdata=args.funcdata, font_size=args.font_size, node_size=args.node_size, move=move, suffixes=args.suffixes, layout_seed=args.layout_seed)

