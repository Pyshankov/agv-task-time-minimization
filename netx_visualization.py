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


def draw_graph(graph, agvs, width = 18):
    
    with graph.lock:
        points = []
        positions = {}
        for cell in graph.cells:
            c = graph.cells[cell]
            points.append((c.x, c.y))
            positions[cell] = (c.x, c.y)

        G = nx.DiGraph()

        def add_edge_to_graph(G, e1, e2, w):
            G.add_edge(e1, e2, weight=w)


        for frm in graph.cell_mappings:
            for to in graph.cell_mappings[frm]: 
                add_edge_to_graph(G, frm, to, 2)

        color_map = []
        positions_labes_names = {}
        positions_labes = {}
        aisle_counter = 1
        operator_counter = 1
        for node in G:

            if graph.cells[node].type in ["OPERATOR_STATION"]:
                    color_map.append('#e0e0eb') 
                    positions_labes[node] = (positions[node][0], positions[node][1] - 0.25)
                    positions_labes_names[node] = f'Operator {operator_counter}'
                    operator_counter = operator_counter + 1
            elif graph.cells[node].type in ["TOTE_PICKUP_STATION"]:
                    color_map.append('#9c9ca4') 
                    positions_labes[node] = (positions[node][0], positions[node][1] + 0.25)
                    positions_labes_names[node] =   f'Aisle {aisle_counter}'
                    aisle_counter = aisle_counter + 1
            else:
              positions_labes[node] = (positions[node][0], positions[node][1])
              positions_labes_names[node] = node
              color_map.append('#FBF8F4')
        
        G3 = nx.DiGraph()
        positions3 = {}
        for x in graph.tote_pickup_stations:
            c = graph.cells[cell]
            positions3[x] = (c.x, c.y + 1)

        G2 = nx.DiGraph()
    
        positions_agv = {}
        positions_agv_arrows = []
        edge_agv_route_map = {}
        agv_color_map = []
        strshow = ""
        for agv in agvs:
            strshow = strshow + f'\n AGV {agv.agv_id}:{agv.color} '
            if agv.task is not None:
                strshow = strshow + f'| TASK: {agv.task.type} {agv.task.status} position: {agv.position} route: {agv.ongoing_route}'

            positions_agv[agv.agv_id] = (agv.x, agv.y)
            positions_agv[agv.agv_id + 100] = (agv.x + float(agv.heading[0])/2, agv.y + float(agv.heading[1])/2)
            G2.add_node(agv.agv_id)
            G2.add_node(agv.agv_id + 100)
            agv_color_map.append(agv.color)
            agv_color_map.append(agv.color)
            positions_agv_arrows.append(agv.color)
            add_edge_to_graph(G2, agv.agv_id, agv.agv_id + 100, 0.1)
            edge_agv_route_map[agv.color] = [ (agv.ongoing_route[idx-1], agv.ongoing_route[idx])  for idx in range(1, len(agv.ongoing_route))]
    
                 
    plt.clf()
    # nx.draw_networkx_nodes(G3, pos=positions, node_size=200, node_color=color_map)
    nx.draw_networkx_nodes(G, pos=positions, node_size=200, node_color=color_map)
    nx.draw_networkx_labels(G, pos=positions_labes, labels = positions_labes_names)
    nx.draw_networkx_nodes(G2, pos=positions_agv, node_size=[0 if v >= 100 else 300 for v in positions_agv],node_shape="s", node_color = agv_color_map)
    # nx.draw_networkx_labels(G2, pos=positions2)
    dashed_edges = graph.edges_adjecent_operator_station_only
    black_edges = [edge for edge in G.edges() if edge not in dashed_edges]
    heading_edges = [edge for edge in G2.edges()]
    weights = nx.get_edge_attributes(G, 'weight').values()
    nx.draw_networkx_edges(G, pos=positions, edgelist=dashed_edges, width=list(weights), edge_color='#7D7C7A',style='dashed', arrows=True)
    nx.draw_networkx_edges(G, pos=positions, edgelist=black_edges, width=list(weights), edge_color='#7D7C7A', arrows=True)
    for color in edge_agv_route_map:
        nx.draw_networkx_edges(G, pos=positions, edgelist=edge_agv_route_map[color], width=2, edge_color=color,style='dashed', arrows=True)
    nx.draw_networkx_edges(G2, pos=positions_agv, edgelist=heading_edges, edge_color=positions_agv_arrows, arrowsize = 20 , arrows=True)

    plt.gca().set_title(strshow, loc='left')
    # plt.gca().margins(1) 
    plt.xlim([-2, width])
    plt.ylim([0, 6])
    plt.show()
    plt.pause(0.001)