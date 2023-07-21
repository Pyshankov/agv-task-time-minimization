import time
import math
import argparse
import imutils
import numpy as np
import sys

import networkx as nx
import numpy as np
from matplotlib import pyplot as plt, animation
import  heapq
import random
from threading import Thread



from model.models import *
from model.warehouse_graph import *
from model.agv import *

def draw_graph2(graph1, agvs, agvs2, agvs3, agvs4, agvs5):
    
    points = []
    positions = {}

    with graph1.lock:

        for cell in graph1.cells:
            c = graph1.cells[cell]
            points.append((c.x, c.y))
            positions[cell] = (c.x, c.y)

        G = nx.DiGraph()

        def add_edge_to_graph(G, e1, e2, w):
            G.add_edge(e1, e2, weight=w)

        for frm in graph1.cell_mappings:
            for to in graph1.cell_mappings[frm]: 
                add_edge_to_graph(G, frm, to, 1)

        color_map = []
        for node in G:
            if graph1.cells[node].type in ["OPERATOR_STATION", "TOTE_PICKUP_STATION"]:
                    color_map.append('#e0e0eb') 
            else:
              color_map.append('#FBF8F4')
        
        red_edges = graph1.edges_adjecent_operator_station_only
        black_edges = [edge for edge in G.edges() if edge not in red_edges]

    G2 = nx.DiGraph()

    positions2 = {}
    color_map2 = ['blue', 'white', 'red', 'white', 'green', 'white', '#C6442A', 'white', 'yellow', 'white']
    for agv in [agvs, agvs2, agvs3, agvs4, agvs5]:
        positions2[agv.agv_id] = (agv.x, agv.y)
        positions2[agv.agv_id + 10] = (agv.x + agv.heading[0], agv.y + agv.heading[1])
        G2.add_node(agv.agv_id)
        G2.add_node(agv.agv_id + 10)
        add_edge_to_graph(G2, agv.agv_id, agv.agv_id + 10, 1)
    green_edges = [edge for edge in G2.edges() if edge not in red_edges]
             
    plt.clf()

    nx.draw_networkx_nodes(G, pos=positions, node_size=300, node_color=color_map)
    # nx.draw_networkx_labels(G, pos=positions)

    nx.draw_networkx_edges(G, pos=positions, edgelist=red_edges, edge_color='r', arrows=True)
    nx.draw_networkx_edges(G, pos=positions, edgelist=black_edges,edge_color='#7D7C7A', arrows=True)

    nx.draw_networkx_nodes(G2, pos=positions2, node_size=400,node_shape="s", node_color = color_map2)
    # nx.draw_networkx_labels(G2, pos=positions2)
    nx.draw_networkx_edges(G, pos=positions2, edgelist=green_edges, edge_color='g', arrows=True)

    plt.show()
    plt.pause(0.001)

def main():
    graph1 = build_graph_v2()


    plt.rcParams["figure.autolayout"] = True
    plt.ion()   

    agv1 = AGV(agv_id = 0) # blue
    graph1.occupy_singe_cell(agv1, cell_id=30)
    task_list1 = [
        Task(agv1.position, [9], type = 'TOTE_PICKUP', tote = Tote(unique_id=1) ),
        Task(9, [48, 54, 57], type = 'TOTE_TO_PERSON'), 
        Task(57, [9], type = 'TOTE_TO_PLACEMENT'),
        Task(9, [agv1.position], type = 'REST_AREA')
    ]

    agv2 = AGV(agv_id = 1) # red
    graph1.occupy_singe_cell(agv2, cell_id=45)
    task_list2 = [
        Task(agv2.position, [9], type = 'TOTE_PICKUP', tote = Tote(unique_id=2) ),
        Task(9, [51], type = 'TOTE_TO_PERSON'), 
        Task(51, [9], type = 'TOTE_TO_PLACEMENT'),
        Task(9, [agv2.position], type = 'REST_AREA')
    ]

    agv3 = AGV(agv_id = 2) # green
    graph1.occupy_singe_cell(agv3, cell_id=44)
    task_list3 = [
        Task(agv3.position, [6], type = 'TOTE_PICKUP', tote = Tote(unique_id=2) ),
        Task(6, [48, 54], type = 'TOTE_TO_PERSON'), 
        Task(54, [6], type = 'TOTE_TO_PLACEMENT'),
        Task(6, [agv3.position], type = 'REST_AREA')
    ]

    agv4 = AGV(agv_id = 3) # yellow
    graph1.occupy_singe_cell(agv4, cell_id=59)
    task_list4 = [
        Task(agv4.position, [6], type = 'TOTE_PICKUP', tote = Tote(unique_id=3) ),
        Task(6, [57], type = 'TOTE_TO_PERSON'), 
        Task(57, [6], type = 'TOTE_TO_PLACEMENT'),
        Task(6, [agv4.position], type = 'REST_AREA')
    ]

    agv5 = AGV(agv_id = 4) # yellow
    graph1.occupy_singe_cell(agv5, cell_id=60)
    task_list5 = [
        Task(agv5.position, [9], type = 'TOTE_PICKUP', tote = Tote(unique_id=4) ),
        Task(9, [48, 54, 57], type = 'TOTE_TO_PERSON'), 
        Task(57, [9], type = 'TOTE_TO_PLACEMENT'),
        Task(9, [agv5.position], type = 'REST_AREA')
    ]

    draw_graph2(graph1, agv1, agv2, agv3, agv4, agv5)

    def start1(graph, agv, task_list):
        # graph, agv, task_list = args
        while len(task_list) > 0:
            print(len(task_list))
            agv.assign_task(task_list.pop(0))
            time.sleep(1)  # wait 1 sec between tasks
            while agv.task.is_finished() is not True:
                agv.execute_task(graph, start_milis = int(round(time.time() * 1000)))
        sys.exit()
        
    # input("Press Enter to continue...")
    Thread(target = start1, args = (graph1, agv1, task_list1)).start()
    Thread(target = start1, args = (graph1, agv2, task_list2)).start()
    Thread(target = start1, args = (graph1, agv3, task_list3)).start()
    Thread(target = start1, args = (graph1, agv4, task_list4)).start()
    Thread(target = start1, args = (graph1, agv5, task_list5)).start()

    while True:
            draw_graph2(graph1, agv1, agv2, agv3, agv4, agv5)
    

if __name__ == '__main__':
    sys.exit(main())


