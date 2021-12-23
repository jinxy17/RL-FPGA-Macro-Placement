from math import exp
import os
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
import numpy as np
from torch.distributions.categorical import Categorical
from Process import *
from Sites import *
from Model_small import *

exp_name = input("Experiment name? ").strip()
os.mkdir("checkpoints/%s" % exp_name)
fout = open("checkpoints/%s/wl_loss.csv" % exp_name, "w")
print("epoch, probability, action-x, action-y, wirelength, critic-value, reward, actor-critic-loss")
print("epoch, probability, action-x, action-y, wirelength, critic-value, reward, actor-critic-loss", file=fout)

p = Process()
s = Sites()
print("=======No cons======")
wl = p.place_and_route()
print("wl:", wl)

x = torch.tensor(np.load("data/x.npy"), dtype=torch.float)
edge_index = torch.tensor(np.load("data/edge_index.npy"), dtype=torch.long)
edge_attr = torch.tensor(np.load("data/edge_attr.npy"), dtype=torch.float)
data = Data(x=x, edge_index=edge_index, edge_attr = edge_attr)
net1 = GCN_small()
net2 = FC_Deconv_small() # policy net
net3 = torch.nn.Linear(108, 1) # value net
# opt = torch.optim.Adam((*net1.parameters(), *net2.parameters()), lr=0.001, weight_decay=5e-4)
opt = torch.optim.Adam((*net2.parameters(), *net3.parameters()), lr=0.001, weight_decay=5e-4)

net1.train()
net2.train()
net3.train()
for epoch in range(2000):
    if epoch % 10 == 0:
        torch.save(net1.state_dict(), "checkpoints/%s/GCN_%d" % (exp_name, epoch))
        torch.save(net2.state_dict(), "checkpoints/%s/FC_Deconv_%d" % (exp_name, epoch))
        torch.save(net3.state_dict(), "checkpoints/%s/Value_%d" % (exp_name, epoch))

    opt.zero_grad()
    x = net1(data)
    x = x[1, :]
    value = net3(x)[0]
    x = net2(x)
    x = x.reshape(100*40)
    x = x / 50.0
    x = F.log_softmax(x, dim=0)
    m = Categorical(logits=x)
    action = int(m.sample())
    action_x = (action // 40) * 25
    action_y = (action % 40) * 25
    loss = - x[action] # RL alg: minimize loss
    assert loss >= 0
    prob = float(torch.exp(-loss))
    wl = p.place_and_route_pblock(s.expand_box(action_x, action_y, 25, 10, {"LUT": 256, "FD": 0, "DSP": 16, "RAMB36": 0, "RAMB18": 0}))
    # reward = 33.5 - wl # should be 34.2398 - wl 
    # reward = (np.mean(wls[-20:]) - wl) / np.std(wls[-20:])
    reward = float(value) - wl # actor-critic
    loss *= reward
    loss += 0.5 * (value - wl) * (value - wl)
    print("%d, %f, %d, %d, %f, %f, %f, %f" % (epoch, prob, action_x, action_y, wl, float(value), reward, float(loss)))
    print("%d, %f, %d, %d, %f, %f, %f, %f" % (epoch, prob, action_x, action_y, wl, float(value), reward, float(loss)), file=fout)
    fout.flush()
    loss.backward()
    opt.step()
    # print("orig prob:", prob)
    # print("updated possibility:", float(F.softmax(net2(net1(data)[1, :]).reshape(100*40))[action]))

p.exit()
fout.close()