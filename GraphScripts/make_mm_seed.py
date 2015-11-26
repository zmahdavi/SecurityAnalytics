import os
import time
import subprocess
import igraph
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import types

def make_adjacency_mm(graph, adjacency_path):
    """Write a MatrixMarket file for the adjacency matrix of a given graph as input for LP in GraphChi.

    Since the edgelist represent an undirected file and graphChi considers directed edges the symmetric
    edge is also written. Also, the node ids must be 1-indexed, thus the + 1 added to igraph node id.

    :param graph:           igraph undirected graph
    :param adjacency_path:  str, a valid path for the output file
    :return:
    """

    n_nodes = len(graph.vs)
    n_edges = len(graph.es)
    mm_header = '%%MatrixMarket matrix coordinate real general\n'  # MatrixMarket header
    with open(adjacency_path, 'w') as adj_f:
        adj_f.write(mm_header)  # 1st line header
        adj_f.write(' '.join([str(n_nodes), str(n_nodes), str(2 * n_edges)]) + '\n')  # 2nd line header
        for edge in graph.es:
            s, t = edge.tuple
            #s, t = s + 1, t + 1  # node ids must be 1-indexed
            adj_f.write('{} {} 1\n{} {} 1\n'.format(s, t, t, s))  # edge and symmetric edge
            #adj_f.write('{} {} 1\n'.format(s, t))


def make_risk_data(graph, seed_frac, node_id_list):
    # seed_ids: list of ids in the seed
    # seeds_subgraph: Subgraph with the seeds
    # A list with the following format:
    # user id (Int), user class (this is id of class like class 1), num_of_neighbours_in_class1, ...,num_of_neighbours_in_classn
    user_risk = []
    check = 0
    for v in graph.vs:
        lineItem = []
        lineItem.append(v["id"])
        #assert(check == v["id"])
        lineItem.append(classify_risk(v["risk_score"]))
        user_risk.append(lineItem)
        check += 1

    n_nodes = len(node_id_list)
    n_seeds = np.round(seed_frac * n_nodes)
    seed_ids = np.random.choice(node_id_list, size=n_seeds, replace=False) #0-indexed igraph ids
    return seed_ids, np.array(user_risk)

def classify_risk(risk_score):
  # risk_score is the risk_score associated with each node, an int between 0 and 100
  # an array that defines the risk_score classes
  #print risk_score
  return 1
  #if risk_score >= 90:
   # return 1
  #elif risk_score <= 100:
    #return 1

def make_seeds_mm(user_risk, seed_id, seeds_path):
    """Write a MatrixMarket file for the seed matrix. Seeds are sampled uniformly at random.

    :param user_and_neib_risk_classes:    np.array(int) (n_nodes, n_classes + 1): risk_score data (see function
    make_risk_data().
    :param nb_risk_classes:      int: number of risk_score classes
    :param seed_frac:           float in [0, 1]:
    :param seeds_path:          str: output file path
    :return:                    np.array(int) (n_nodes,): 0-indexed seed ids
                                np.array(int) (n_nodes,): corresponding risk_score classes
                                np.array(int): (n_classes, n_classes): conditional distribution of neighbor risk_score class given user risk_score class
    """

    seed_and_class_list = user_risk[seed_id, 0] # First column is the user ids
    seed_risk_classes = user_risk[seed_id, 1] # Second column is user's risk_score class

    # seed_ids must be 1-indexed for GraphChi and risk_score classes also
    seeds_to_write = np.column_stack((seed_and_class_list , seed_risk_classes , np.ones(len(seed_id), dtype=int)))
    seeds_to_write = pd.DataFrame(seeds_to_write)
    print "len(seed_ids)=", len(seed_id)
    print "Seed path: ", seeds_path

    #mm_header = '%%MatrixMarket matrix coordinate real general\n'  # MatrixMarket header
    with open(seeds_path, 'w') as seeds_f:
        seeds_to_write.to_csv(seeds_f, sep=' ', header=False, index=False)

    return seed_risk_classes

def loadtxt_fast(filename, dtype=np.int32, skiprows=0, delimiter=' '):
    def iter_func():
        with open(filename, 'r') as infile:
            for _ in range(skiprows):
                next(infile)
            skip = 0
            for line in infile:
                line = line.rstrip().split(delimiter)
                for item in line:
                    yield dtype(item)

    data = np.fromiter(iter_func(), dtype=dtype)
    return data

def get_node_ids(graph):
    node_id_list = []
    for v in graph.vs:
      node_id_list.append(v["id"])
    return node_id_list

def main():
    
    # ###### PATHS and PARAMETERS ###########
    start = time.time()
    attribute = 'risk_score'
    # if you make change to this you have to make change to other functions
    #risk_class_boundaries = [90]  # list of boundaries, see header for more explanation
    n_classes = 1
    #seed_fractions =  np.logspace(-5, -0.02, num=30)
    #seed_fractions = np.concatenate(([.001, .003, .01, .03,.10], np.logspace(-1, -0.03, num=25)))
    seed_fractions = [0.1]
    n_iter = 1


    # ###### PATHS ###########
    #graph_path = '/datadrive/reza/ndata/Toy/NewToy.graphml'
    graph_path = '/sampa/home/zeinab/NData/totalNetwork.graphml'

    dir, basename = os.path.split(graph_path)
    basename = os.path.splitext(basename)[0]
    lp_path = os.path.join(dir, 'LP', attribute)
    if not os.path.exists(lp_path):
        os.makedirs(lp_path)
    adjacency_path = os.path.join(lp_path, basename)

    # Load graph
    print("\nLoading network from file", graph_path)
    graph = igraph.Graph.Read_GraphML(graph_path)
    node_id_list = []
    for v in graph.vs:
      v["id"] = v.index
      node_id_list.append(v["id"])


    ####### WRITE ADJACENCY INPUT FILES ##############
    print("\nWriting adjacency MatrixMarket file:\n", adjacency_path)
    make_adjacency_mm(graph, adjacency_path)
    print("file size: {:.1f} MB".format(os.path.getsize(adjacency_path) / 1e6))
    startload = time.time()

    # At this strisk the variable user_and_neib_risk_classes is an numpy array where each row correspond
    # to a user (ordered by their index value), the first column represents the user risk_score class and the
    # following columns represent the number of neighbor in each of the risk_score classes.
    # Example: the row '2 0 2 16 8 0 0' means that the corresponding user belongs to risk_score class 2 and
    # has 20 neighbors, 2 of them in risk_score class 1, 16 in risk_score class 2 and 8 in risk_score class 3.

    n_nodes = len(node_id_list)
    print "nb of nodes =", n_nodes
    stopload = time.time()
    print "***** loading or generating risk_score data duration ={:.1f}s".format(stopload - startload)

    for i, seed_frac in enumerate(seed_fractions):
        seed_ids, user_risk = make_risk_data(graph, seed_frac, node_id_list)
        for j in xrange(n_iter):
            startiter = time.time()
            print "################################################"
            print "#", seed_frac, "iter", j
            seeds_path = os.path.join(lp_path, str(seed_frac) + basename + '.seeds1')

            # ###### WRITE SEED INPUT FILE for GRAPHCHI ########
            print "\nWriting seed MatrixMarket file:\n", seeds_path
            seed_risk_classes = make_seeds_mm(user_risk, seed_ids, seeds_path)


if __name__ == "__main__":
    main()
