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



from model.models import *
from model.warehouse_graph import *
from model.agv import *

def draw_graph(graph1):
    points = []
    positions = {}
    for cell in graph1.cells:
      x = ((cell-1) % 10) 
      y = int((cell-1)/10)
      points.append((x,7-y))
      positions[cell] = (x,7-y)
          
    G = nx.DiGraph()
    
    def add_edge_to_graph(G, e1, e2, w):
        G.add_edge(e1, e2, weight=w)

    for frm in graph1.cell_mappings:
        for to in graph1.cell_mappings[frm]: 
            add_edge_to_graph(G, frm, to, 1)
    
    color_map = []
    for node in G:
        if graph1.cells[node].occupied_agv is not None:
            color_map.append('blue')
        elif graph1.cells[node].tote is not None:
          color_map.append('green')
        elif graph1.cells[node].occupied_agv is not None and graph1.cells[node].occupied_agv.tote is not None:
          color_map.append('red')
        else:
          color_map.append('white')

    plt.clf()
    nx.draw(G, pos=positions, node_size=500, node_color=color_map, arrows=True)
    nx.draw_networkx_labels(G, pos=positions)
    plt.show()
    plt.pause(0.001)

def draw_graph2(graph1):
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
        if graph1.cells[node].occupied_agv is not None:
            color_map.append('blue')
        elif graph1.cells[node].tote is not None:
          color_map.append('green')
        elif graph1.cells[node].occupied_agv is not None and graph1.cells[node].occupied_agv.tote is not None:
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
    plt.rcParams["figure.autolayout"] = True
    plt.ion()   

    agv1 = AGV(agv_id = 0, velocity = 5)
    agv2 = AGV(agv_id = 1, velocity = 5)
    agv3 = AGV(agv_id = 2, velocity = 5)

    agv1.assign_position(graph1, 30)
    agv2.assign_position(graph1, 45)
    agv3.assign_position(graph1, 60)

    draw_graph2(graph1)

    agv3.assign_task(Task(agv3.position, 3, type = 'TOTE_PICKUP'))
    agv2.assign_task(Task(agv2.position, 6, type = 'TOTE_PICKUP'))
    agv1.assign_task(Task(agv1.position, 9, type = 'TOTE_PICKUP'))
    route1 = agv1.execute_task(graph1, sleep = True)
    route2 = agv2.execute_task(graph1, sleep = True)
    route3 = agv3.execute_task(graph1, sleep = True)
    while len(route1 + route2 +route3)!=0:
        route1 = agv1.execute_task(graph1, sleep = True)
        print(route1)
        print(agv1.position)
        draw_graph2(graph1)

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)
        draw_graph2(graph1)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        draw_graph2(graph1)


    agv3.assign_task(Task(agv3.position, 48, type = 'TOTE_TO_PERSON'))
    agv1.assign_task(Task(agv1.position, 51, type = 'TOTE_TO_PERSON'))
    agv2.assign_task(Task(agv2.position, 57, type = 'TOTE_TO_PERSON'))
    route1 = agv1.execute_task(graph1, sleep = True)
    route2 = agv2.execute_task(graph1, sleep = True)
    route3 = agv3.execute_task(graph1, sleep = True)
    while len(route1 + route2 +route3)!=0:
        route1 = agv1.execute_task(graph1, sleep = True)
        print(route1)
        print(agv1.position)
        draw_graph2(graph1)

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)
        draw_graph2(graph1)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        draw_graph2(graph1)
    
    agv3.assign_task(Task(agv3.position, 3, type = 'TOTE_TO_PLACEMENT'))
    agv2.assign_task(Task(agv2.position, 6, type = 'TOTE_TO_PLACEMENT'))
    agv1.assign_task(Task(agv1.position, 9, type = 'TOTE_TO_PLACEMENT'))
    route1 = agv1.execute_task(graph1, sleep = True)
    route2 = agv2.execute_task(graph1, sleep = True)
    route3 = agv3.execute_task(graph1, sleep = True)
    while len(route1 + route2 +route3)!=0:
        route1 = agv1.execute_task(graph1, sleep = True)
        print(route1)
        print(agv1.position)
        draw_graph2(graph1)

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)
        draw_graph2(graph1)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        draw_graph2(graph1)


    agv1.assign_task(Task(agv1.position, 30, type = 'TOTE_PICKUP'))
    agv3.assign_task(Task(agv3.position, 45, type = 'TOTE_PICKUP'))
    agv2.assign_task(Task(agv2.position, 60, type = 'TOTE_PICKUP'))
    route1 = agv1.execute_task(graph1, sleep = True)
    route2 = agv2.execute_task(graph1, sleep = True)
    route3 = agv3.execute_task(graph1, sleep = True)
    while len(route1 + route2 +route3 )!=0:
        route1 = agv1.execute_task(graph1, sleep = True)
        print(route1)
        print(agv1.position)
        draw_graph2(graph1)

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)
        draw_graph2(graph1)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        draw_graph2(graph1)
    


def main1():
    graph1 = build_graph_v1()
    plt.rcParams["figure.autolayout"] = True
    plt.ion()

    # graph = WarehouseGraph(cells = range(0,4), directed_edges = [(0,1, 10.0), (1,2, 4.0), (0,2, 15.0), (2,3, 15.0)])
    # print(graph.bfs(0,2))

    # print(graph1.bfs(16, 63))
    # print(graph1.bfs(63, 16))

    agv1 = AGV(agv_id = 0, velocity = 5)
    agv2 = AGV(agv_id = 1, velocity = 5)
    agv3 = AGV(agv_id = 2, velocity = 5)

    agv1.assign_position(graph1, 70)
    agv2.assign_position(graph1, 50)
    agv3.assign_position(graph1, 60)

    draw_graph(graph1)

    agv3.assign_task(Task(agv3.position, 13, type = 'TOTE_PICKUP'))
    agv2.assign_task(Task(agv2.position, 17, type = 'TOTE_PICKUP'))
    agv1.assign_task(Task(agv1.position, 16, type = 'TOTE_PICKUP'))
    route1 = agv1.execute_task(graph1, sleep = True)
    route2 = agv2.execute_task(graph1, sleep = True)
    route3 = agv3.execute_task(graph1, sleep = True)
    while len(route1 + route2 +route3)!=0:
        route1 = agv1.execute_task(graph1, sleep = True)
        print(route1)
        print(agv1.position)
        draw_graph(graph1)

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)
        draw_graph(graph1)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        draw_graph(graph1)


    agv3.assign_task(Task(agv3.position, 67, type = 'TOTE_TO_PERSON'))
    agv1.assign_task(Task(agv1.position, 63, type = 'TOTE_TO_PERSON'))
    agv2.assign_task(Task(agv2.position, 65, type = 'TOTE_TO_PERSON'))
    route1 = agv1.execute_task(graph1, sleep = True)
    route2 = agv2.execute_task(graph1, sleep = True)
    route3 = agv3.execute_task(graph1, sleep = True)
    while len(route1 + route2 +route3)!=0:
        route1 = agv1.execute_task(graph1, sleep = True)
        print(route1)
        print(agv1.position)
        draw_graph(graph1)

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)
        draw_graph(graph1)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        draw_graph(graph1)


    agv3.assign_task(Task(agv3.position, 13, type = 'TOTE_TO_PLACEMENT'))
    agv1.assign_task(Task(agv1.position, 16, type = 'TOTE_TO_PLACEMENT'))
    agv2.assign_task(Task(agv2.position, 17, type = 'TOTE_TO_PLACEMENT'))
    route1 = agv1.execute_task(graph1, sleep = True)
    route2 = agv2.execute_task(graph1, sleep = True)
    route3 = agv3.execute_task(graph1, sleep = True)
    while len(route1 + route2 +route3 )!=0:
        route1 = agv1.execute_task(graph1, sleep = True)
        print(route1)
        print(agv1.position)
        draw_graph(graph1)

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)
        draw_graph(graph1)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        draw_graph(graph1)



if __name__ == '__main__':
    sys.exit(main())


