import random

from mininet.log import lg
from ripl.dctopo import StructuredTopo
from ripl.dctopo import StructuredNodeSpec
from ripl.dctopo import StructuredEdgeSpec

class Node(object):
    def __init__(self, num_ports=4, id=0):
        self.num_ports = num_ports
        self.id = id


# Topology to be instantiated in Mininet
class JellyfishTopo(StructuredTopo):
    LAYER_EDGE = 2
    LAYER_HOST = 3

    def __init__(self, seed=0, switches=16, nodes=4, ports_per_switch=4,
               hosts_per_switch=1, bw=40):
        self.bw = bw  # bandwidth 
        self.id = 0
        
        # self.id_gen = JellyfishNodeID
        random.seed(seed)

        edge_specs = [StructuredEdgeSpec(bw)] * 3
        node_specs = [StructuredNodeSpec(ports_per_switch - hosts_per_switch,
                                        hosts_per_switch, bw, bw, 'edge'),
                    StructuredNodeSpec(1, 0, bw, None, 'host'),
                    ]

        super(JellyfishTopo, self).__init__(node_specs, edge_specs)

        self.create_topology(switches, nodes, ports_per_switch, hosts_per_switch)

    def def_nopts(self, layer, name=None):
        '''Return default dict for a FatTree topo.
        @param layer layer of node
        @param name name of node
        @return d dict with layer key/val pair, plus anything else (later)
        '''
        d = {'layer': layer}
        if name:
            id = self.id_gen(name=name)
            # For hosts only, set the IP
            if layer == self.LAYER_HOST:
                d.update({'ip': id.ip_str()})
                d.update({'mac': id.mac_str()})
            d.update({'dpid': "%016x" % id.dpid})
            return d

    

    def not_fully_connected(self, switch_list, link_list):
        for i in range(len(switch_list)):
            switch = switch_list[i]
            for j in range(i + 1, len(switch_list)):
                switch2 = switch_list[j]
                link = (switch, switch2)
                if link not in link_list and (switch2, switch) not in link_list:
                    return True
            return False

    def addHosts(self, switches, nodes, ports_per_switch, hosts_per_switch):
        switch_num = 1
        host_list = []

        for num in range(0, nodes):
            host_id = self.id_gen(num+1, num+1).name_str()
            host_opts = self.def_nopts(self.LAYER_HOST, host_id)
            h = self.addHost(host_id, **host_opts)
            lg.debug("Adding host: %s\n" % (host_id))
            host_list.append(h)

            if num % hosts_per_switch == 0:
                switch_id = self.id_gen(switch_num, 255).name_str()
                switch_opts = self.def_nopts(self.LAYER_EDGE, switch_id)
                switch = self.addSwitch(switch_id, **switch_opts)
                lg.debug("Adding switch: %s\n" % (switch_id))

                for host in host_list:
                    self.addLink(host, switch, bw=self.bw)
                    lg.debug("Adding link: %s to %s\n" % (str(host), str(switch)))
                    host_list = []
                    switch_num += 1

        for num in range(nodes / hosts_per_switch, switches):
            switch_id = self.id_gen(num+1, 255).name_str()
            lg.debug("Adding switch: %s\n" % (switch_id))
            switch_opts = self.def_nopts(self.LAYER_EDGE, switch_id)
            switch = self.addSwitch(switch_id, **switch_opts)

    def count_links_with_switch(self, switch, link_list):
        count = 0
        for link in link_list:
        if switch in link:
            count += 1
        return count

    def up_nodes(self, name):
        '''Return edges one layer higher (closer to core).
        @param name name
        @return names list of names
        '''
        return [n for n in self.g[name] if self.isSwitch(n)]

    def down_nodes(self, name):
        '''Return edges one layer higher (closer to hosts).
        @param name name
        @return names list of names
        '''
        layer = self.layer(name) + 1
        nodes = [n for n in self.g[name] if self.layer(n) == layer]
        return nodes

    def switch_is_fully_connected(self, switch, links, switches):
        for s in switches:
            if s == switch:
                continue
            if (switch, s) not in links or (s, switch) not in links:
                return False
            return True

    def create_topology(self, switches, nodes, ports_per_switch, hosts_per_switch):
        self.addHosts(switches, nodes, ports_per_switch, hosts_per_switch)
        switch_list = list(self.switches())
        added_links = []

        while len(switch_list) > 1 and self.not_fully_connected(switch_list, added_links):
            switch = random.choice(switch_list)
            switch2 = random.choice(switch_list)
            if switch == switch2:
                continue
            link = (switch, switch2)
            if link in added_links or (switch2, switch) in added_links:
                continue
            added_links.append(link)
            if (self.count_links_with_switch(switch, added_links) == ports_per_switch or
                self.switch_is_fully_connected(switch, added_links, switch_list)):
                switch_list.remove(switch)
            if (self.count_links_with_switch(switch2, added_links) == ports_per_switch or
                self.switch_is_fully_connected(switch2, added_links, switch_list)):
                switch_list.remove(switch2)

        print(added_links)
        print (switch_list)

        while True:
            completed = True
            for switch in switch_list:
                if self.switch_is_fully_connected(switch, added_links, switch_list):
                    continue
                if self.count_links_with_switch(switch, added_links) < (ports_per_switch - 1):
                    completed = False
                    link = random.choice(added_links)
                    if switch == link [0] or switch == link[1]:
                        continue
                    new_link1 = (switch, link[0])
                    new_link2 = (switch, link[1])
                    added_links.remove(link)
                    added_links.append(new_link1)
                    added_links.append(new_link2)
            if completed:
                break

        for link in added_links:
            self.addLink(link[0], link[1], bw=self.bw)

topos = {'jellyfish': JellyfishTopo}

if __name__ == '__main__':
    pass