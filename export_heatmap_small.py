from re import I
import torch
import torch.nn.functional as F
from torch_geometric.data import Data
import numpy as np
from torch.distributions.categorical import Categorical
from Process import *
from Sites import *
from Model_small import *


x = torch.tensor(np.load("data/x.npy"), dtype=torch.float)
edge_index = torch.tensor(np.load("data/edge_index.npy"), dtype=torch.long)
edge_attr = torch.tensor(np.load("data/edge_attr.npy"), dtype=torch.float)
data = Data(x=x, edge_index=edge_index, edge_attr = edge_attr)
net1 = GCN_small()
net2 = FC_Deconv_small()
exp_name = input("Experiment name? ").strip()

for i in range(0, 2000, 10):
    net1.load_state_dict(torch.load("checkpoints/%s/GCN_%d" % (exp_name, i)))
    net1.eval()
    net2.load_state_dict(torch.load("checkpoints/%s/FC_Deconv_%d" % (exp_name, i)))
    net2.eval()

    x = net1(data)
    x = x[1, :]
    x = net2(x)
    x = x.reshape(100*40)
    x = x / 50.0
    x = F.softmax(x, dim=0).reshape(100, 40)
    np.save("checkpoints/%s/heat_map_%d.npy" % (exp_name, i), x.detach().numpy())
