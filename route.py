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
    for cell in graph1.cells:
      x = ((cell-1) % 10) 
      y = int((cell-1)/10)
      points.append((x,7-y))
    
    G = nx.Graph()
    
    def add_edge_to_graph(G, e1, e2, w):
        G.add_edge(e1, e2, weight=w)

    for frm in graph1.cell_mappings:
        for to in graph1.cell_mappings[frm]: 
            add_edge_to_graph(G, points[frm-1], points[to-1], 1)

    # you want your own layout
    pos = nx.spring_layout(G)
    pos = {point: point for point in points}

    # add axis
    fig, ax = plt.subplots()
    nx.draw(G, pos=pos, node_size=500, node_color='k', ax=ax, arrows=True)  # draw nodes and edges
    nx.draw_networkx_labels(G, pos=pos)  # draw node labels/names


    plt.axis("on")
    ax.set_xlim(-1, 10)
    ax.set_ylim(-1, 10)
    ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
    plt.show()
    

def main():
    graph1 = build_graph_v1()

    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True
    fig = plt.figure()
    G = nx.DiGraph()
    G.add_nodes_from(graph1.cells)
    nx.draw(G, with_labels=True)

    def animate(frame):
        fig.clear()
        num1 = random.randint(0, 4)
        num2 = random.randint(0, 4)
        G.add_edges_from([(num1, num2)])
        nx.draw(G, with_labels=True)

    # ani = animation.FuncAnimation(fig, animate, frames=1, interval=1000, repeat=True)
    # plt.show()
    # exit()

    # graph = WarehouseGraph(cells = range(0,4), directed_edges = [(0,1, 10.0), (1,2, 4.0), (0,2, 15.0), (2,3, 15.0)])
    # print(graph.bfs(0,2))

    # print(graph1.bfs(16, 63))
    # print(graph1.bfs(63, 16))

    agv1 = AGV(agv_id = 0, velocity = 3)
    agv2 = AGV(agv_id = 1, velocity = 3)
    agv3 = AGV(agv_id = 2, velocity = 3)

    agv1.assign_position(graph1, 70)
    agv2.assign_position(graph1, 50)
    agv3.assign_position(graph1, 60)

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

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        time.sleep(1)

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

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        time.sleep(1)

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

        route2 = agv2.execute_task(graph1, sleep = True)
        print(route2)
        print(agv2.position)

        route3 = agv3.execute_task(graph1, sleep = True)
        print(route3)
        print(agv3.position)
        print()
        time.sleep(1)


if __name__ == '__main__':
    sys.exit(main())


