import time
import math
import argparse
import imutils
import numpy as np
import sys




from model.models import *

def main():
    graph = WarehouseGraph(cells = range(0,4), directed_edges = [(0,1, 10.0), (1,2, 4.0), (0,2, 15.0), (2,3, 15.0)])
    print(graph.bfs(0,3))

if __name__ == '__main__':
    sys.exit(main())


