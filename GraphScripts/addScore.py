import igraph
import numpy as np
import networkx as nx

#graph_path = '/datadrive/reza/ndata/Toy.graphml'
graph_path = '/sampa/home/zeinab/NData/nDataAllEdges.graphml'
graph = igraph.Graph.Read_GraphML(graph_path)
for v in graph.vs:
        risk_scores = np.random.randint(1, high = 100, size = graph.vcount())
        graph.vs["risk_score"] = risk_scores

igraph.Graph.write_graphml(graph, "/sampa/home/zeinab/NData/nDataAllEdgeswithRiskScore.graphml")