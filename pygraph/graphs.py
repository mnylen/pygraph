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


class Digraph(object):
    nodes = dict

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
                
                for k in digraph.nodes[i]:
                    if j == k: continue

                    if matrix.get(i, j) == 1 and matrix.get(j, k) == 1:
                        # If this happens it means there are edges i -> j and
                        # j -> k. Because this is an acyclic closure, we
                        # therefore have also edge i -> k, which can be
                        # removed as redundant.
                        
                        if not remove.has_key(i): remove[i] = set()
                        remove[i].add(k)
                        matrix.set(i, k, 0)
                    

        for node in remove:
            digraph.nodes[node] -= remove[node]