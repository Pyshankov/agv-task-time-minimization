

from model.models import *
from model.warehouse_graph import *

#TODO create warehouse with 10 stations
def build_graph_n_stations(pickup_stations = 10): 
    rows = 4
    cols = 3 * (pickup_stations + 1)
    cell_indx = range(1, rows*cols+1)
    directed_edges = []

    operator_stations = []
    tote_pickup_stations = []
    edges_adjecent_operator_station_only = []
    for i in range(1, pickup_stations+1):
        tote_pickup_stations.append(i * 3)
        operator_stations.append(cols + cols + cols + i * 3)
        if i < pickup_stations:
            edges_adjecent_operator_station_only.append((cols + cols + cols + i * 3, cols + cols + cols + i * 3 + 1))

    # to left only:  
    for idx in range (cols+2, 2*cols+1): 
        directed_edges.append((idx, idx - 1, 1))

    # to right:  
    for idx in range (2*cols+2, 3*cols+1): 
        directed_edges.append((idx - 1, idx, 1))
    
    # to right:  
    for idx in range (3*cols+2, 4*cols+1): 
        directed_edges.append((idx - 1, idx, 1))
    
    for p in tote_pickup_stations:
        directed_edges.append((p, p + cols, 1))
        directed_edges.append((cols + p, p, 1))

        directed_edges.append((cols + cols + cols + p, cols + cols + p, 1))
        if p > 3:
            directed_edges.append((cols + cols + p - 1 , cols + cols + cols + p - 1, 1))

        if p < pickup_stations * 3:
            directed_edges.append((cols + cols + p + 1, cols + p + 1 ,1))
            directed_edges.append((cols + p + 2, cols + cols + p + 2 ,1))

    directed_edges.append((cols + 1, cols + cols + 1, 1))
    directed_edges.append(( cols + cols + 1, cols + cols + cols + 1, 1))
    
    directed_edges.append((cols + cols + cols , cols + cols , 1))
    directed_edges.append((cols + cols + cols + cols, cols + cols + cols, 1))

    directed_edges.append((cols + cols + cols - 1, cols + cols - 1, 1))
    directed_edges.append((cols + cols + cols + cols - 1, cols + cols + cols - 1, 1))

    directed_edges.append((cols + cols + cols - 2, cols + cols - 2, 1))
    directed_edges.append((cols + cols + cols + cols - 2, cols + cols + cols - 2, 1))

    graph = WarehouseGraph(cells = cell_indx, \
        shape = (cols, rows), \
        directed_edges = directed_edges, \
        operator_stations = operator_stations, \
        tote_pickup_stations = tote_pickup_stations, \
        edges_adjecent_operator_station_only = edges_adjecent_operator_station_only \
            )

    for idx in graph.tote_pickup_stations:
        graph.cells[idx].tote = Tote(idx)
        graph.cells[idx].occupied_tote = True    

    return graph
