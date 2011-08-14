import unittest
import pygraph.graphs as graphs

class TestSubgraphs(unittest.TestCase):
    def setUp(self):
        self.a = graphs.NamedNode("A")
        self.b = graphs.NamedNode("B")
        self.c = graphs.NamedNode("C")
        self.d = graphs.NamedNode("D")
        
        self.dg = graphs.Digraph()
        self.dg.add_edge(self.a, self.b)
        self.dg.add_edge(self.b, self.c)
        self.dg.add_edge(self.c, self.d)

    def test_creates_subgraph(self):
        dg = self.dg.subgraph(self.b)

        self.assertEquals(3, len(dg.nodes_set()))
        self.assertEquals(2, len(dg.edges()))
        self.assertTrue(dg.has_edge(self.b, self.c))
        self.assertTrue(dg.has_edge(self.c, self.d))

    def test_creates_subgraph_without_edges(self):
        dg = self.dg.subgraph(self.d)

        self.assertEquals(1, len(dg.nodes_set()))
        self.assertEquals(0, len(dg.edges()))
        self.assertTrue(self.d in dg.nodes_set())