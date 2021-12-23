import numpy as np
import math
class Sites:
    def __init__(self, load=True):
        if not load:
            self.process_data()
        self.accu_sum = np.load("data/accu_sum.npy", allow_pickle=True)
        self.nearest_forward = np.load("data/nearest_forward.npy", allow_pickle=True)
        self.nearest = np.load("data/nearest.npy", allow_pickle=True)

    def process_data(self):
        img = np.zeros((2500, 1000, 3), dtype=int)
        color = {"SLICE": (0, 255, 0), "DSP48E2": (255, 0, 0), "RAMB36": (255, 255, 0), "RAMB18": (0, 255, 255),}
        sitemap = []
        ign = set()
        with open('data/design.sites', 'r') as fin:
            for line in fin:
                t, x, y = line.split()
                tt = t.split("_")[0]
                x = int(x)
                y = int(y)
                if tt in color:
                    sitemap.append((x, y, t))
                else:
                    ign.add(tt)
        print("ignored:", ign)
        sitemap = sorted(sitemap, key=lambda x: (x[0], x[1]))
        from tqdm import tqdm
        nearest = np.zeros((2500, 1000, 4), dtype="object")
        accu_sum = np.zeros((2500, 1000, 4), dtype=int)
        for x, y, t in tqdm(sitemap):
            if t[:5] == "SLICE":
                nearest[x:, y: , 0] = t
                accu_sum[x:, y:, 0] += 1
            elif t[:5] == "DSP48":
                nearest[x:, y: , 1] = t
                accu_sum[x:, y:, 1] += 1
            elif t[:5] == "RAMB3":
                nearest[x:, y: , 2] = t
                accu_sum[x:, y:, 2] += 1
            else:
                assert t[:5] == "RAMB1"
                nearest[x:, y: , 3] = t
                accu_sum[x:, y:, 3] += 1
        nearest_forward = np.zeros((2500, 1000, 4), dtype="object")
        sitemap.reverse()
        for x, y, t in tqdm(sitemap):
            if t[:5] == "SLICE":
                nearest_forward[:x, :y , 0] = t
            elif t[:5] == "DSP48":
                nearest_forward[:x, :y , 1] = t
            elif t[:5] == "RAMB3":
                nearest_forward[:x, :y , 2] = t
            else:
                assert t[:5] == "RAMB1"
                nearest_forward[:x, :y , 3] = t
        sitemap.reverse()
        np.save("data/accu_sum.npy", accu_sum)
        np.save("data/nearest_forward.npy", nearest_forward)
        np.save("data/nearest.npy", nearest)
    
    def get_range(self, x1, y1, x2, y2):
        ret = []
        for i in range(4):
            if self.nearest_forward[x1, y1, i] and self.nearest[x2, y2, i]:
                ret.append(self.nearest_forward[x1, y1, i] + ":" + self.nearest[x2, y2, i]) 
        return " ".join(ret)
    
    def get_count(self, x1, y1, x2, y2):
        return self.accu_sum[x2, y2, :] - self.accu_sum[x1, y2, :] - self.accu_sum[x2, y1, :] + self.accu_sum[x1, y1, :]

    def expand_box(self, x_avg, y_avg, w, h, used, util=0.80):
        while True:
            x1 = max((x_avg - w // 2, 0))
            x2 = min((x_avg + w // 2, 2499))
            y1 = max((y_avg - h // 2, 0))
            y2 = min((y_avg + h // 2, 999))
            # print(x1, y1, x2, y2)
            count = self.get_count(x1, y1, x2, y2)
            if (util * count[0] * 8 >= used["LUT"]) and \
                (util * count[0] * 16 >= used["FD"]) and \
                (util * count[1] >= used["DSP"]) and \
                (util * count[2] >= used["RAMB36"]) and \
                (util * count[3] >= used["RAMB18"]):
                break
            else:
                w = math.ceil(w * 1.1)
                h = math.ceil(h * 1.1)
        # print(self.get_range(x1, y1, x2, y2))
        # print(self.get_count(x1, y1, x2, y2))
        return self.get_range(x1, y1, x2, y2)

if __name__ == "__main__":
    s = Sites()
    print(s.expand_box(500, 500, 25, 10, {"LUT": 256, "FD": 0, "DSP": 16, "RAMB36": 0, "RAMB18": 0}))