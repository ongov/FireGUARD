"""Makes the size bar charts for the maps"""
from __future__ import print_function

import logging
import math
import sys

import matplotlib.pyplot as plt
import pandas as pd
## HACK: disable warnings about this
pd.options.mode.chained_assignment = None

from util import fixK

def makeSizeGraphName(f):
    """!
    Make path for size graph based on path for CSV
    @param f Path to csv to use for generating path
    @return Path to save size graph to
    """
    return f.replace('.csv', '.png')

def makeSizeGraph(f, for_day):
    """!
    Make size graph from simulation results
    @param f Path to csv to use for generating path
    @param for_day Day of simulation to make graph for
    @return Path size graph was saved to
    """
    graph_png = makeSizeGraphName(f)
    logging.debug("Making size graph {}".format(graph_png))
    #~ print(f)
    df = pd.read_csv(f)
    logging.debug("Read {}".format(f))
    df.columns = ['size']
    #~ print(df)
    stats = {}
    # make statistics about how often sizes are at least each power of 10
    stats[0] = float(len(df.query('size == 1'))) / len(df) * 100
    for x in xrange(5):
        s = math.pow(10, x)
        stats[int(s)] = float(len(df.query('size > {} and size <= {}'.format(s, s * 10)))) / len(df) * 100
    s = math.pow(10, 5)
    stats[int(s)] = float(len(df.query('size > {}'.format(s)))) / len(df) * 100
    ds = pd.DataFrame(stats, index=[0]).transpose().reset_index()
    ds.columns = ['size', 'pct_of']
    ds['ranges'] = ds.apply(lambda x: '>{}\n- {}'.format(fixK(x['size']), fixK(x['size'] * 10)), axis=1)
    ds['ranges'][0] = '1'
    ds['ranges'][len(ds['ranges']) - 1] = '>{}'.format(fixK(s))
    #~ print(ds)
    #~ out_file = f.replace('sizes', 'stats')
    #~ ds.to_csv(out_file, index=False)
    p = ds.plot(kind='bar', x='ranges', y='pct_of', color='red', legend=None, figsize=(5, 5), width=0.95, ylim=(0, 100))
    #~ plt.rcParams.update({'font.size': 15})
    plt.title('Simulation Sizes by Day {}'.format(for_day))
    plt.xlabel('Size (ha)')
    plt.ylabel('Percent with given size')
    for item in p.axes.get_xticklabels():
        item.set_rotation(0)
    labels = list(ds['ranges'])
    def fixPos(v):
        if v >= 95:
            return v - 5
        return max(0, int(v) + 1)
    for i, v in enumerate(ds['pct_of']):
        x = i - 0.35 if (v >= 10 or round(v) < 0.1) else i - 0.25
        text = "<0.1%" if (v > 0 and round(v) < 0.1) else "{:0.1f}%".format(v) if v < 100 else '100%'
        plt.text(x, fixPos(v), text, color='black', fontweight='bold', fontsize=10)
    plt.tight_layout()
    #~ print(graph_png)
    logging.debug("Saving size graph {}".format(graph_png))
    plt.savefig(graph_png)
    plt.close("all")
    return graph_png

if __name__ == "__main__":
    if len(sys.argv) != 3:
        logging.fatal("Invalid arguments: {}".format(sys.argv))
        sys.exit(-1)
    makeSizeGraph(sys.argv[1], sys.argv[2])
