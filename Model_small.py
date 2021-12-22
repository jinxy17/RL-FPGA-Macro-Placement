
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

class GCN_small(torch.nn.Module):
    def __init__(self, features_in=9, hidden1=18, hidden2=54, features_out=108):
        super().__init__()
        self.conv1 = GCNConv(features_in, hidden1)
        self.conv2 = GCNConv(hidden1, hidden2)
        self.conv3 = GCNConv(hidden2, features_out)

    def forward(self, data):
        x, edge_index, edge_weight = data.x, data.edge_index, data.edge_attr.view(-1)
        x = self.conv1(x, edge_index, edge_weight)
        x = F.relu(x)
        # x = F.dropout(x, training=self.training)
        x = self.conv2(x, edge_index, edge_weight)
        x = F.relu(x)
        # x = F.dropout(x, training=self.training)
        x = self.conv3(x, edge_index, edge_weight)
        x = F.relu(x)
        return x
        # return F.log_softmax(x, dim=1)

class FC_Deconv_small(torch.nn.Module):
    def __init__(self, features_in=108):
        super().__init__()
        self.fc = nn.Linear(features_in, 8*12*5)
        self.deconv1 = nn.ConvTranspose2d(in_channels=8, out_channels=4, kernel_size=3, stride=2)
        self.deconv2 = nn.ConvTranspose2d(in_channels=4, out_channels=2, kernel_size=3, stride=2)
        self.deconv3 = nn.ConvTranspose2d(in_channels=2, out_channels=1, kernel_size=3, stride=2)

    def forward(self, x):
        # x.shape: (features_in, )
        assert len(x.shape) == 1
        x = self.fc(x).reshape(1, 8, 12, 5)
        x = F.relu(x)
        x = self.deconv1(x)
        x = F.relu(x)
        x = self.deconv2(x)
        x = F.relu(x)
        x = self.deconv3(x)
        x = x.squeeze(0).squeeze(0)
        x = x[2: 2+100, 3: 3+40]
        return x

if __name__ == "__main__":
    import numpy as np
    from torch_geometric.data import Data
    x = torch.tensor(np.load("data/x.npy"), dtype=torch.float)
    edge_index = torch.tensor(np.load("data/edge_index.npy"), dtype=torch.long)
    edge_attr = torch.tensor(np.load("data/edge_attr.npy"), dtype=torch.float)
    data = Data(x=x, edge_index=edge_index, edge_attr = edge_attr)
    net1 = GCN_small()
    net2 = FC_Deconv_small()
    x = net1(data)[1, :]
    print(net2(x).shape)