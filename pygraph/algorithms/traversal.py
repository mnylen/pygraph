from pygraph.core import *

class NodeVisitor(Node):
    def visit_node(self, dg, v):
        pass

    def visit_edge(self, dg, v, w):
        pass

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
    visited   = set()
    stack.append(root)
    cancelled = False

    while len(stack) > 0:
        top = stack.pop()

        if not top in visited:
            if visitor is not None:
                visitor.visit_node(digraph, top)

            if continue_lambda is not None:
                if not continue_lambda(top):
                    cancelled = True
                    break

            for adjacent_node in digraph.nodes[top]:
                if visitor is not None:
                    visitor.visit_edge(digraph, top, adjacent_node)

                stack.append(adjacent_node)

    return cancelled