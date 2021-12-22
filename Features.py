import numpy as np

class Features:
    def __init__(self, nodes="data/design.nodes", nets="data/design.nets"):
        # self.nodes = []
        self.nodedict = {}
        node_types = set()
        with open(nodes) as fin:
            for line in fin:
                line = line.split()
                if line[1][:4] == "DSP_" or line[1] == "INBUF" or line[1] == "IBUFCTRL":
                    continue
                # self.nodes.append((line[0], line[1]))
                self.nodedict[line[0]] = [line[1], -1]
                node_types.add(line[1])
        print("imported %d nodes" % len(self.nodedict))
        print(node_types)

        self.nets = []
        with open(nets) as fin:
            while True:
                line = fin.readline()
                if not line: 
                    break
                assert line.strip() == "net"
                s = set()
                n = []
                while True:
                    line = fin.readline()
                    line = line.split()
                    if line[0] == "endnet":
                        break
                    # assert line[0] in self.nodedict
                    if line[0] not in self.nodedict: # DSP_XXX, INBUF, IBUFCTRL
                        line[0] = "/".join(line[0].split("/")[:-1])
                    assert line[0] in self.nodedict
                    s.add(line[0])
                    n.append(line[0])
                if len(s) > 1:
                    self.nets.append(tuple(n))
        print("imported %d nets" % len(self.nets))
    
    def cluster(self):
        self.cluster = set()
        for n in self.nodedict.keys():
            n = n.split("/")
            if len(n) == 1:
                self.cluster.add("__root__")
            else:
                self.cluster.add(n[0])
        self.cluster = sorted(list(self.cluster))
        for n in self.nodedict.keys():
            ns = n.split("/")
            if len(ns) == 1:
                self.nodedict[n][1] = self.cluster.index("__root__")
            else:
                self.nodedict[n][1] = self.cluster.index(ns[0])
        
    def extract(self):
        # node features
        self.features = []
        for i in range(len(self.cluster)):
            self.features.append({"LUT": 0, "FD": 0, "DSP": 0, \
                    "RAMB36": 0, "RAMB18": 0, "boundary_nets": 0, \
                    "placed": 0, "x": 0, "y": 0})
                    # "IBUF": 0, "OBUF": 0, "BUFGCE": 0, "CARRY8": 0, })
        for [t, c] in self.nodedict.values():
            if t[:3] == "LUT":
                self.features[c]["LUT"] += 1
            elif t[:2] == "FD":
                self.features[c]["FD"] += 1
            elif t[:3] == "DSP":
                self.features[c]["DSP"] += 1
            elif t[:6] == "RAMB36":
                self.features[c]["RAMB36"] += 1
            elif t[:6] == "RAMB18":
                self.features[c]["RAMB18"] += 1
            # elif t[:4] == "IBUF":
            #     self.features[c]["IBUF"] += 1
            # elif t[:4] == "OBUF":
            #     self.features[c]["OBUF"] += 1
            # elif t[:6] == "BUFGCE":
            #     self.features[c]["BUFGCE"] += 1
            # elif t[:6] == "RAMB18":
            #     self.features[c]["RAMB18"] += 1
            # elif t[:6] == "CARRY8":
            #     self.features[c]["CARRY8"] += 1
            # else:
            #     assert False
        # edge features
        self.edge_features = {}
        # import numpy as np
        # np.set_printoptions(linewidth=100)
        # mat = np.zeros((21, 21), dtype=int)'''
        for i in range(len(self.cluster)):
            for j in range(i+1, len(self.cluster)):
                self.edge_features[(i, j)] = 0
                self.edge_features[(j, i)] = 0
        for net in self.nets:
            s = {self.nodedict[n][1] for n in net}
            if len(s) > 1:
                for i in s:
                    self.features[i]["boundary_nets"] += 1
                    for j in s:
                        if j != i:
                            self.edge_features[(i, j)] += 1
                            # mat[i, j] += 1
        for u, v in zip(self.cluster, self.features):
            print(u, v)
        # print(self.edge_features)
    
    def export(self):
        num_nodes = len(self.cluster)
        num_features = len(self.features[0])
        num_edges = num_nodes * (num_nodes - 1)
        num_edge_features = 1
        x = np.zeros((num_nodes, num_features))
        edge_index = np.zeros((2, num_edges), dtype=int)
        edge_attr = np.zeros((num_edges, num_edge_features))
        for i in range(num_nodes):
            x[i] = (self.features[i]['LUT'], self.features[i]['FD'], self.features[i]['DSP'], \
                    self.features[i]['RAMB36'], self.features[i]['RAMB18'], self.features[i]['boundary_nets'], \
                    self.features[i]["placed"], self.features[i]["x"], self.features[i]["y"])
                    # self.features[i]['IBUF'], self.features[i]['OBUF'], \
                    # self.features[i]['BUFGCE'], , self.features[i]['CARRY8'], \
        for i, (u, v) in enumerate(self.edge_features.items()):
            edge_index[:, i] = u
            edge_attr[i] = v
        # print(x)
        # print(edge_index)
        # print(edge_attr)
        np.save("data/x.npy", x)
        np.save("data/edge_index.npy", edge_index)
        np.save("data/edge_attr.npy", edge_attr)
        
if __name__ == "__main__":
    f = Features()
    f.cluster()
    f.extract()
    f.export()
