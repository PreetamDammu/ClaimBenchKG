import networkx as nx
import matplotlib.pyplot as plt

def plot_triplets_graph(triplets):
    """
    Parameters:
    - triplets: A list of triplets where each triplet consists of (source, relation, target)
    """
    G = nx.DiGraph()
    for src, rel, tgt in triplets:
        G.add_edge(src, tgt, relation=rel)


    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)  


    nx.draw_networkx_nodes(G, pos, node_size=700)
    nx.draw_networkx_edges(G, pos, width=2)
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): d['relation'] for u, v, d in G.edges(data=True)})
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

    plt.axis('off')
    plt.show() 

    return
