import subprocess, re
from Sites import *

class Process:
    def __init__(self):
        self.process = subprocess.Popen(["vivado", "-mode", "tcl", "-nojournal", "-nolog", "-source", "tcl/init.tcl"], \
                            stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True, bufsize=0)
        self.wait_for_complete()
        print("vivado initialized")
        self.process.stdin.write("open_checkpoint data/post_synth_xcvu095.dcp\n")
        self.process.stdin.write("puts complete!!\n")
        self.process.stdin.flush()
        self.wait_for_complete()
        print("checkpoint opened")
    
    def place_and_route(self):
        self.process.stdin.write("place_design -no_timing_driven\n")
        self.process.stdin.write("route_design -no_timing_driven\n")
        self.process.stdin.write("route_design -unroute\n")
        self.process.stdin.write("place_design -unplace\n")
        self.process.stdin.write("puts complete!!\n")
        self.process.stdin.flush()
        output = self.wait_for_complete()
        return self.get_util(output)

    def place_and_route_pblock(self, str):
        self.process.stdin.write("create_pblock pblock_arnd1\n")
        self.process.stdin.write("resize_pblock pblock_arnd1 -add {%s}\n" % str)
        self.process.stdin.write("add_cells_to_pblock pblock_arnd1 [get_cells [list arnd1]] -clear_locs\n")
        self.process.stdin.write("place_design -no_timing_driven\n")
        self.process.stdin.write("route_design -no_timing_driven\n")
        self.process.stdin.write("route_design -unroute\n")
        self.process.stdin.write("place_design -unplace\n")
        self.process.stdin.write("delete_pblock [get_pblocks  pblock_arnd1]\n")
        self.process.stdin.write("puts complete!!\n")
        self.process.stdin.flush()
        output = self.wait_for_complete()
        return self.get_util(output)

    def exit(self):
        print("exiting...")
        self.process.stdin.write("exit\n")
        self.process.stdin.flush()
        self.wait_for_exit()


    def wait_for_complete(self):
        ret = ""
        while True:
            output = self.process.stdout.readline().strip()
            if output[:5] == "ERROR" or output[:8] == "CRITICAL":
                print(">>>>", output)
            ret += output + "\n"
            if output == "complete!!":
                break
        return ret

    def wait_for_exit(self):
        while True:
            output = self.process.stdout.readline().strip()
            print(">>>>", output)
            return_code = self.process.poll()
            if return_code is not None:
                print("====exec finished====")
                break
        
    def get_util(self, output):
        r = re.compile(r"Global Vertical Routing Utilization\s*=\s*([0-9]*\.?[0-9]*)\s*%\s*Global Horizontal Routing Utilization\s*=\s*([0-9]*\.?[0-9]*)\s*%")
        vutil, hutil = r.findall(output)[-1]
        vutil = float(vutil)
        hutil = float(hutil)
        return vutil * 100 + hutil * 100






