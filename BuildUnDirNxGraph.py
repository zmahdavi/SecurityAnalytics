import numpy as np
import networkx as nx
import csv
from types import *

class Result:
    nodeId = None
    egoNetGraph = None
    egoNetDegree = 0
    nofEdges = 0
    totalWeight = 0
    eigenValue = 0.0
    deg_cent = None
    betw_cent = None
    clustering_coeff = None
    eigenvector_cent = None

    # This is used to write to CSv file
    def get_properties_sequence(self):
        return [self.nodeId, str(nx.nodes(self.egoNetGraph)), str(self.egoNetDegree) , str(self.nofEdges) , str(self.deg_cent), str(self.betw_cent), str(self.clustering_coeff)]

    def __str__(self):
        return "NodeId: " + self.nodeId + "Ego-net Graph" + str(nx.nodes(self.egoNetGraph)) + ", Degree: " + str(self.egoNetDegree) + " , Edges: " + str(self.nofEdges) + " centerality: " + str(self.deg_cent) + ", " + str(self.betw_cent) + ", " \
        + str(self.clustering_coeff)

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

def create_graph_features(g):
    assert type(g) is not NoneType
    print "starting calculating graphcut features."
    deg_cent_dic = nx.degree_centrality(g)
    betw_cent_dic = nx.betweenness_centrality(g)
    clustering_coeff_dic = nx.clustering(g, weight = None)
#    eigenvector_cent_list = nx.eigenvector_centrality(g, weight = None)

    egoNetList = []
    for n in nx.nodes_iter(g):
        resultObj = Result()
        resultObj.nodeId = n
        resultObj.egoNetGraph = nx.ego_graph(g, n, radius=1, center=True, undirected=False, distance=None)
        resultObj.egoNetDegree = nx.number_of_nodes(resultObj.egoNetGraph)
        resultObj.nofEdges = nx.number_of_edges(resultObj.egoNetGraph)

        # Assigning graph cut features
        resultObj.deg_cent = deg_cent_dic[n]
        resultObj.betw_cent = betw_cent_dic[n]
        resultObj.clustering_coeff = clustering_coeff_dic[n]
        # resultObj.eigenvector_cent = eigenvector_cent_list[n]
        egoNetList.append(resultObj)

    return egoNetList

# We don't need this anymore
"""
def create_graphcut_features(g):
    deg_cent = nx.degree_centrality(g)
    betw_cent = nx.betweenness_centrality(g)
    clustering_coeff = nx.clustering(g, weight = None)
    eigenvector_cent = nx.eigenvector_centrality(g, weight = None)
"""

"""#Create a Networkx graph from list of source and destination tuples
def make_graph(g, edge_tuples):
    g.add_edges_from(edge_tuples)"""

def write_results_to_csv(results, fileName):
    assert type(results) is ListType
    assert type(fileName) is StringType
    with open(fileName, 'wb') as target:
        writer = csv.writer(target)
        # prints header
        writer.writerow(["NodeId", "Ego-net Graph", "Ego-net degree", "Ego-net Edges", "centerality degree", "between centerality", "clustering_coeff"])
        for item in results:
            seq = item.get_properties_sequence()
            writer.writerow(seq)



def main():
    file_path =  '/sampa/home/zeinab/NData/10k'
    g = nx.Graph() #for making an undirected graph
    edges = get_src_dest(read_file(file_path))
    g.add_edges_from(edges)
    resultList = create_graph_features(g)
    write_results_to_csv(resultList, "/sampa/home/zeinab/NData/10kresult.csv")
    """for node in resultList:
       print node"""

if __name__ == "__main__":
    main()
