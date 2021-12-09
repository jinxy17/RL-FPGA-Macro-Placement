# RL-FPGA-Macro-Placement
Solve FPGA macro placement using reinforcement learning.

This is an ongoing project.


Features.py: perform clustering & feature extraction on netlist

Model.py: stochastic policy net - GNN followed by de-conv

Process.py: call Xilinx Vivado in subprocess to place and route

Sites.py: xcvu095 site extraction and pblock expansion

export_heatmap.py: extract heatmap of policy net during training process

train.py: training script using pytorch
