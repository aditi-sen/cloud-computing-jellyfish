"""Custom topologies for Mininet

author: Brandon Heller (brandonh@stanford.edu)

To use this file to run a RipL-specific topology on Mininet.  Example:

  sudo mn --custom ~/ripl/ripl/mn.py --topo ft,4
"""

from ripl.dctopo import FatTreeTopo, JellyFishTopo #, VL2Topo, TreeTopo

topos = { 'ft': FatTreeTopo, 'jf': JellyFishTopo}
#,
#          'vl2': VL2Topo,
#          'tree': TreeTopo }
