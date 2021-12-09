from math import exp
import os
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
import numpy as np
from torch.distributions.categorical import Categorical
from Process import *
from Sites import *
from Model import *

exp_name = input("Experiment name? ").strip()
os.mkdir("data/%s" % exp_name)
fout = open("data/%s/wl_loss.csv" % exp_name, "w")

p = Process()
s = Sites()
print("=======No cons======")
wl = p.place_and_route()
print("current wl:", wl)

x = torch.tensor(np.load("data/x.npy"), dtype=torch.float)
edge_index = torch.tensor(np.load("data/edge_index.npy"), dtype=torch.long)
edge_attr = torch.tensor(np.load("data/edge_attr.npy"), dtype=torch.float)
data = Data(x=x, edge_index=edge_index, edge_attr = edge_attr)
net1 = GCN()
net2 = FC_Deconv()
# opt = torch.optim.Adam((*net1.parameters(), *net2.parameters()), lr=0.001, weight_decay=5e-4)
opt = torch.optim.Adam(net2.parameters(), lr=0.001, weight_decay=5e-4)

net1.train()
net2.train()
wls = []
for epoch in range(2000):
    print("=======  RL %d ======" % epoch)
    if epoch % 5 == 0:
        torch.save(net1.state_dict(), "data/%s/GCN_%d" % (exp_name, epoch))
        torch.save(net2.state_dict(), "data/%s/FC_Deconv_%d" % (exp_name, epoch))

    opt.zero_grad()

    x = net1(data)
    x = x[1, :]
    x = net2(x)
    x = x.reshape(250*100)
    x = F.log_softmax(x, dim=0)
    m = Categorical(logits=x)
    action = int(m.sample())
    # action = 18574
    action_x = (action // 100) * 10
    action_y = (action % 100) * 10
    print("current action:", action_x, action_y)
    loss = - x[action] # RL alg: minimize loss
    assert loss >= 0
    print("current possibility:", float(torch.exp(-loss)))
    wl = p.place_and_route_pblock(s.expand_box(action_x, action_y, 25, 10, {"LUT": 256, "FD": 0, "DSP": 16, "RAMB36": 0, "RAMB18": 0}))
    print("current wl:", wl)
    wls.append(wl)
    if len(wls) == 1: 
        continue
    # reward = 33.5 - wl # should be 34.2398 - wl 
    reward = (np.mean(wls[-20:]) - wl) / np.std(wls[-20:])
    print("current reward:", reward)
    loss *= reward
    print("current loss:", loss)
    print("%f, %f" % (wl, float(loss)), file=fout)
    fout.flush()
    loss.backward()
    opt.step()
    print("updated possibility:", F.softmax(net2(net1(data)[1, :]).reshape(250*100))[action])

p.exit()
fout.close()