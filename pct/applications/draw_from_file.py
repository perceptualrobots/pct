


import argparse
from os import sep, makedirs
from pct.hierarchy import PCTHierarchy


def drawit(filename=None, outdir=None, move=None, funcdata=False, font_size=6, node_size=200, suffixes=False):
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

    hpct.draw(file=draw_file, move=move, with_edge_labels=True, font_size=font_size, node_size=node_size, funcdata=funcdata)
    print('Image saved to '+draw_file)

    if hpct.consolidate():
        move={}
        draw_file = outdir + sep + 'draw-' + input_filename.replace('.properties', '_consolidate.png')
        hpct.draw(file=draw_file, move=move, with_edge_labels=True, font_size=font_size, node_size=node_size, funcdata=funcdata)
        print('Image saved to '+draw_file)


"""
Examples:

python -m pct.applications.draw_from_file -s -f "C:/Users/ryoung/Versioning/python/nbdev/pct/nbs/testfiles/MountainCar/MountainCar-cdf7cc1497ad143c0b04a3d9e72ab783.properties" -o "/tmp" -m "{'IV':[0, 0.05],'IP':[-0.6, 0.3],  'OL0C0sm':[-0.28, -0.2],'OL0C1sm':[0.28, -0.2], 'OL1C0sm':[0,-0.1], 'MountainCarContinuousV0':[-.7,-0.5], 'Action1ws':[-0.4,-0.3]}"


{'IV':[0, 0.05],'IP':[-0.6, 0.3],  'OL0C0sm':[-0.28, -0.2],'OL0C1sm':[0.28, -0.2], 'OL1C0sm':[0,-0.1], 'MountainCarContinuousV0':[-.7,-0.5], 'Action1ws':[-0.4,-0.3]}
{'IV':[0, 0.05],'IP':[-0.6, 0.3],  'OL0C0sm':[-0.28, -0.2],'OL0C1sm':[0.28, -0.2], 'OL1C0sm':[0,-0.1], 'MountainCarContinuousV0':[-.7,-0.5], 'Action1ws':[-0.4,-0.3]},
            

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

    args = parser.parse_args()

    if args.move is None:
        move = {}
    else:
        move = eval(args.move)

    drawit(filename=args.file, outdir=args.outdir, funcdata=args.funcdata, font_size=args.font_size, node_size=args.node_size, move=move, suffixes=args.suffixes)

