from pygraph.core import *

def topsort(dg):
    return TopologicalSort(dg).run()


class TopologicalSort(object):
    digraph = Digraph

    def __init__(self, digraph):
        self.digraph = digraph.copy()

    def run(self):
        order = list()
        nodes = self.__find_nodes_without_incoming_edges()

        while len(nodes) > 0:
            n = nodes.pop()
            order.append(n)

            adjacent_nodes = list(self.digraph.nodes[n])

            for m in adjacent_nodes:
                self.digraph.remove_edge(n, m)


                if len(self.digraph.incoming[m]) == 0:
                    nodes.append(m)

        if len(self.digraph.edges()) > 0:
            raise RuntimeError, "Graph has at least one cycle. May be you forgot to use StrongComponents.quotient?"

        return order

    def __find_nodes_without_incoming_edges(self):
        nodes = list()

        for node in self.digraph.incoming:
            if len(self.digraph.incoming[node]) == 0:
                nodes.append(node)

        return nodes