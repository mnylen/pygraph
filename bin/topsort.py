import sys
sys.path.append("../pygraph")

if len(sys.argv) < 2:
    print "GRAPHFILE must be given. Check --usage"
    exit(1)

import pygraph.graphs as graphs
dg = graphs.Digraph.from_file(sys.argv[1])
dg = graphs.Transitivity.reduce(dg)

order = graphs.TopologicalSort(dg).run()
for node in order:
    print str(node)
