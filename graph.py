import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from networkx.readwrite import json_graph
import math

def draw_graph(G, **options):
    print json_graph.node_link_data(G)
    ranks = options.get('rank')
    pos = options.get('pos', nx.spring_layout)
    fname = "graphs/{0}".format(options.get('file_name', 'out_default.png'))
    pos = pos(G, scale=1, iterations=40, k=0.35)
    if not ranks:
        node_size = 100
    else:
        node_size = [abs(math.log(ranks[k])) * 500 for k in G.nodes()]

    color_rank = {}
    for rank, key in enumerate(sorted(ranks, key=lambda x: ranks[x])):
        color_rank[key] = rank
    edge_weights = [abs(math.log(data['weight']))/2.0 for n1, n2, data in G.edges(data=True)]
#    cNorm = colors.Normalize(vmin=0, vmax=1)
#    scalarMap = cmx.ScalarMappable(norm=cNorm, cmap='Greys')
    nx.draw_networkx_nodes(G, pos, node_size=node_size, node_color=[color_rank[key] for key in G.nodes()], linewidths=0.5, cmap=plt.cm.Blues, alpha=0.8)
    nx.draw_networkx_edges(G, pos, width=edge_weights, alpha=0.4, edge_color="grey")
    nx.draw_networkx_labels(G, pos, font_size=8, font_family='sans-serif')
    print "saving {0}".format(fname)
    plt.axis('off')
    plt.savefig(fname)
