class Node(object):
    """
    Represents a node in a graph.

    """
    pass


class NamedNode(Node):
    """
    Represents a named node in a graph.

    """
    name = str
    
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.name


class ComponentNode(Node):
    """
    Represents a component in a graph.

    """

    nodes = set

    def __init__(self, nodes = None):
        if nodes is None: nodes = set()
        self.nodes = nodes

    def __str__(self):
        return "__".join(map(lambda x: str(x), self.nodes))

class Digraph(object):
    nodes   = dict
    nodemap = None
    
    def __init__(self):
        self.nodes = dict()

    def add_edge(self, from_node, to_node):
        self.add_node(from_node)
        self.add_node(to_node)
        
        self.nodes[from_node].add(to_node)

    def add_node(self, node):
        if not self.nodes.has_key(node):
            self.nodes[node] = set()

    def has_edge(self, from_node, to_node):
        return self.nodes.has_key(from_node) and to_node in self.nodes[from_node]

    def edges(self):
        edges = set()

        for node in self.nodes:
            for adjacent_node in self.nodes[node]:
                edges.add( (node, adjacent_node) )

        return edges

    def nodes_set(self):
        return set(self.nodes.keys())

    def to_dot(self):
        dot = "digraph {\n"

        for v in self.nodes_set():
            if len(self.nodes[v]) == 0:
                dot += "\t%s;" % str(v)
            else:
                for w in self.nodes[v]:
                    dot += "\t%s -> %s;\n" % (str(v), str(w))

        dot += "}\n"
        
        return dot


    @staticmethod
    def from_file(filename):
        f = None
        dg = Digraph()
        
        try:
            f = open(filename, "r")

            for line in f.readlines():
                parts = line.split(":")

                node_name = ""
                edge_target_list_str = ""

                if len(parts) > 1:
                    node_name, edge_target_list_str = parts
                else:
                    node_name = parts[0]

                dg.add_node(NamedNode(node_name))
                for edge_target_name in edge_target_list_str.strip().split(" "):
                    dg.add_edge(NamedNode(node_name), NamedNode(edge_target_name))
        finally:
            if f:
                f.close()

        return dg

class ByteNodeMatrix(object):
    matrix = dict

    def __init__(self):
        self.matrix = dict()

    def set(self, i, j, b):
        """
        @i: Node
        @j: Node
        @b: anything
        
        Sets given byte to edge i -> j

        """

        if not self.matrix.has_key(i):
            self.matrix[i] = dict()
        
        self.matrix[i][j] = b

    def get(self, i, j):
        """
        @i: Node
        @j: Node

        Gets value for edge i -> j, or -1 if the matrix does not contain such edge.
        
        """
        
        if self.matrix.has_key(i) and self.matrix[i].has_key(j):
            return self.matrix[i][j]
        else:
            return -1


class Traversal(object):
    @staticmethod
    def dfs(digraph, root, visitor = None, continue_lambda = None):
        """
        @digraph: Digraph
        @root: Node
        @visitor: NodeVisitor
        @continue_lambda: lambda

        Performs depth first search on digraph starting from given root node. If
        continue_lambda has been given, performs it for each new node found by
        traversing the digraph. If the lambda returns False, traversing of the
        digraph will be cancelled. Useful for checking, for example, if node j
        is reachable from node i.

        returns boolean indicating whether the dfs cancelled or not.
        
        """

        stack     = list()
        visited   = dict()
        stack.append(root)
        cancelled = False

        while len(stack) > 0:
            top = stack.pop()

            if not visited.has_key(top):
                visited[top] = True

                if visitor is not None:
                    visitor(root)

                if continue_lambda is not None:
                    if not continue_lambda(top):
                        cancelled = True
                        break

                for adjacent_node in digraph.nodes[top]:
                    stack.append(adjacent_node)

        return cancelled

    
class Transitivity(object):
    @staticmethod
    def acyclic_closure(digraph):
        """
        @digraph: Digraph

        Generates reachability matrix for an acyclic digraph.

        Reachability matrix allows for constant time querying
        of whether node i can reach node j in a digraph.
        
        """
        
        matrix = ByteNodeMatrix()

        for i in digraph.nodes_set():
            for j in digraph.nodes_set():
                reaches = (i == j) or Traversal.dfs(digraph, i, None, lambda v: v != j)
                
                if reaches:
                    matrix.set(i, j, 1)
                else:
                    matrix.set(i, j, 0)

        return matrix

    @staticmethod
    def acyclic_reduce(digraph):
        """
        @digraph: Digraph

        Removes redundant edges from a acyclic digraph. The time complexity
        of the actual algorithm for G = (V, E) is O(|V|*|V|*|E|).

        """

        remove = dict()
        matrix  = Transitivity.acyclic_closure(digraph)

        for i in digraph.nodes_set():
            for j in digraph.nodes[i]:
                if i == j: continue
                if not matrix.get(i, j): continue
                
                for k in digraph.nodes[i]:
                    if j == k: continue

                    if matrix.get(j, k) == 1:
                        # If this happens it means there are edges i -> j and
                        # j -> k. Because this is an acyclic closure, we
                        # therefore have also edge i -> k, which can be
                        # removed as redundant.
                        
                        if not remove.has_key(i): remove[i] = set()
                        remove[i].add(k)
                        matrix.set(i, k, 0)

        for node in remove:
            digraph.nodes[node] -= remove[node]

    @staticmethod
    def reduce(digraph):
        """
        @digraph: Digraph

        Returns quotient digraph G' from the digraph G with redundant
        edges removed. Check G'.nodemap for mapping of nodes in G to nodes
        in G'.
        
        """

        quotient = StrongComponents(digraph).quotient()
        Transitivity.acyclic_reduce(quotient)

        return quotient

class StrongComponents(object):
    digraph    = Digraph
    stack      = list
    index      = 0
    lowlinks   = dict
    indexes    = dict
    nodemap    = dict
    quotient   = Digraph
    in_stack   = set
    components = set
    
    def __init__(self, digraph):
        self.digraph = digraph

    def run(self):
        self.stack      = list()
        self.lowlinks   = dict()
        self.indexes    = dict()
        self.index      = 0
        self.components = set()
        self.in_stack   = set()
        self.nodemap    = dict()

        for node in self.digraph.nodes_set():
            if not self.indexes.has_key(node):
                self.__strong_connect(node)

    def __strong_connect(self, v):
        self.indexes[v]  = self.index
        self.lowlinks[v] = self.index
        self.index += 1
        self.stack.append(v)
        self.in_stack.add(v)
        
        for w in self.digraph.nodes[v]:
            if not self.indexes.has_key(w):
                self.__strong_connect(w)
                self.lowlinks[v] = min(self.lowlinks[v], self.lowlinks[w])
            elif w in self.stack:
                self.lowlinks[v] = min(self.lowlinks[v], self.indexes[w])

        if self.lowlinks[v] == self.indexes[v]:
            component_nodes = set()
            while True:
                w = self.stack.pop()
                self.in_stack.remove(w)
                component_nodes.add(w)

                if w == v:
                    break
            
            component = ComponentNode(component_nodes)
            for node in component_nodes:
                self.nodemap[node] = component

            self.components.add(component)

    def quotient(self):
        self.run()

        quotient = Digraph()
        quotient.nodemap = self.nodemap.copy()

        for c in self.components:
            quotient.add_node(c)

            for v in c.nodes:
                for w in self.digraph.nodes[v]:
                    c2 = self.nodemap[w]
                    if c2 != c:
                        quotient.add_edge(c, c2)


        return quotient
