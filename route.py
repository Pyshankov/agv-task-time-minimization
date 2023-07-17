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

def draw_graph2(graph1, agvs, agvs2):
    points = []
    positions = {}
    for cell in graph1.cells:
      x = ((cell-1) % 15) 
      y = int((cell-1)/15)
      points.append((x,4-y))
      positions[cell] = (x,4-y)
          
    G = nx.DiGraph()
    
    def add_edge_to_graph(G, e1, e2, w):
        G.add_edge(e1, e2, weight=w)

    for frm in graph1.cell_mappings:
        for to in graph1.cell_mappings[frm]: 
            add_edge_to_graph(G, frm, to, 1)
    
    color_map = []
    for node in G:
        if graph1.cells[node].unique_id == agvs.position:
                color_map.append('blue') 
        elif graph1.cells[node].unique_id == agvs2.position:
                color_map.append('red') 
        else:
          color_map.append('white')

    plt.clf()
    nx.draw(G, pos=positions, node_size=500, node_color=color_map, arrows=True)
    nx.draw_networkx_labels(G, pos=positions)
    plt.show()
    plt.pause(0.001)

def main():
    graph1 = build_graph_v2()
    # print(graph1.bfs(12, 3))

    plt.rcParams["figure.autolayout"] = True
    plt.ion()   

    agv1 = AGV(agv_id = 0)
    # graph1.occupy_singe_cell(agv1, cell_id=30)
    agv1.assign_position(30)

    agv2 = AGV(agv_id = 1)
    agv2.assign_position(45)
    # graph1.occupy_singe_cell(agv2, cell_id=45)

    draw_graph2(graph1, agv1, agv2)


    task = Task(agv1.position, [9, 48, 54, 45], type = 'TOTE_PICKUP', tote = Tote(unique_id=1) )
    task2 = Task(agv2.position, [9, 48, 54, 30], type = 'TOTE_PICKUP', tote = Tote(unique_id=1) )
    agv1.assign_task(task)
    agv2.assign_task(task2)

    def start1():
        while task.is_finished() is not True:
            agv1.execute_task(graph1)
    
    def start2():
        while task2.is_finished() is not True:
            agv2.execute_task(graph1)



    Thread(target = start1).start()
    Thread(target = start2).start()

    while True:
            draw_graph2(graph1, agv1, agv2)



if __name__ == '__main__':
    sys.exit(main())


