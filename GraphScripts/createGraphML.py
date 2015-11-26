import csv
import igraph
import networkx as nx
import matplotlib.pyplot as plt

def read_csv(csvPath):
    with open(csvPath) as f:
        edge_tuples = [tuple(line) for line in csv.reader(f)]
    return edge_tuples

def make_graph(graph, edge_tuples):
    graph.add_edges_from(edge_tuples)

def main():
    #csvPath = './total_edg'
    csvPath =  '/sampa/home/zeinab/NData/RawData/nDataEdges'
    #plotPath = '/datadrive/reza/ndata/http_https_ipsec'
    edge_tuples = read_csv(csvPath)
    g = nx.DiGraph()
    make_graph(g, edge_tuples)
    #nx.draw(g)
    #plt.savefig(plotPath)
    nx.write_graphml(g, ".graphml", prettyprint=True)

if __name__ == "__main__":
    main()
