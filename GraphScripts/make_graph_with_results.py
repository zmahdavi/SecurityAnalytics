import igraph
import numpy as np
import csv

def read_seed(seed_file): 
    with open(seed_file, 'r') as fin:
        reader = csv.reader(fin, delimiter = ' ')
        all = []
        for row in reader: 
            all.append(row)
        np_seed_list = np.array(all)
        seed_ids = np_seed_list[:, 0] # First column is the user ids
    return seed_ids

def read_mm(output_file):
    with open(output_file, 'r') as fin:
        reader = csv.reader(fin, delimiter = ' ')
        all = []
        for row in reader: 
            all.append(row)
        np_list = np.array(all)
    return np_list

def main():
    graph_path = '/sampa/home/zeinab/NData/totalNetwork.graphml'
    graph = igraph.Graph.Read_GraphML(graph_path)
    seed_file = '/sampa/home/zeinab/NData/LP/risk_score/0.1totalNetwork.seeds1'
    output_file = '/sampa/home/zeinab/NData/LP/risk_score/0.1totalNetworkwithRiskScore.mm-2'
    seed_ids = read_seed(seed_file)
    lp_result = read_mm(output_file)
    for v in graph.vs:
        v["id"] = v.index
        v["seed"] = 0 
    for seed in seed_ids:
        graph.vs[int(seed)]["seed"] = 1
    for node in lp_result:
        graph.vs[int(node[0])]["risk_score"] = int(node[1])
    igraph.Graph.write_graphml(graph, "/sampa/home/zeinab/NData/LP/risk_score/allEdgesIter2.graphml")

if __name__ == "__main__":
    main()
