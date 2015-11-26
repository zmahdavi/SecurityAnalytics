import numpy as np
import networkx as nx
import csv

class Result:
    egoNetGraph = None
    egoNetDegree = 0
    nofEdges = 0
    totalWeight = 0
    eigenValue = 0.0
    def __str__(self):
        return "Ego-net Graph" + str(nx.nodes(self.egoNetGraph)) + ", Degree: " + str(self.egoNetDegree) + " , Edges: " + str(self.nofEdges)
    
#Read the input file and put it in a Python list
def read_file(file_path):
    with open(file_path) as f:
        lines = f.read().splitlines()
    return lines

# A function to extract an individual set of sources and destinations
def get_src_dest(lines):
    src = []
    dest = []
    for row in lines:
        columns = row.split(',')
        src.append(columns[2])
        dest.append(columns[3])
        edge_tuples = zip(src,dest)
    return edge_tuples

def create_egonet_features(g):
    egoNetList = []
    for n in nx.nodes_iter(g):
        resultObj = Result()
        resultObj.egoNetGraph = nx.ego_graph(g, n, radius=1, center=True, undirected=False, distance=None)
        resultObj.egoNetDegree = nx.number_of_nodes(resultObj.egoNetGraph)
        resultObj.nofEdges = nx.number_of_edges(resultObj.egoNetGraph)
        egoNetList.append(resultObj)
 #       print resultObj
    return egoNetList


"""#Create a Networkx graph from list of source and destination tuples
def make_graph(g, edge_tuples):
    g.add_edges_from(edge_tuples)"""

"""def calculate_features(gml_graph):
    deg_cent = nx.degree_centrality(gml_graph)
    betw_cent = nx.betweenness_centrality(gml_graph)"""

def main():
    file_path =  '/sampa/home/zeinab/NData/10k'
    g = nx.DiGraph() #for making a directed graph
    edges = get_src_dest(read_file(file_path))
    g.add_edges_from(edges)
    egoNetList = create_egonet_features(g)
    for node in egoNetList:
       print node

if __name__ == "__main__":
    main()
