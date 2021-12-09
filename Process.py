import subprocess, re
from Sites import *


def wait_for_complete():
    ret = ""
    while True:
        output = process.stdout.readline().strip()
        if output[:5] == "ERROR" or output[:8] == "CRITICAL":
            print(">>>>", output)
        ret += output + "\n"
        if output == "complete!!":
            break
    return ret

def wait_for_exit():
    while True:
        output = process.stdout.readline().strip()
        print(">>>>", output)
        return_code = process.poll()
        if return_code is not None:
            print("====exec finished====")
            break
    
def get_util(output):
    r = re.compile(r"Global Vertical Routing Utilization\s*=\s*([0-9]*\.?[0-9]*)\s*%\s*Global Horizontal Routing Utilization\s*=\s*([0-9]*\.?[0-9]*)\s*%")
    vutil, hutil = r.findall(output)[-1]
    vutil = float(vutil)
    hutil = float(hutil)
    return vutil * 480 + hutil * 168




process = subprocess.Popen(["vivado", "-mode", "tcl", "-nojournal", "-nolog", "-source", "tcl/open_checkpoint.tcl"], \
                            stdout=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines=True, bufsize=0)
wait_for_complete()

s = Sites()

print("place and route #1")
process.stdin.write("source tcl/place_and_route.tcl\n")
process.stdin.flush()
output = wait_for_complete()
print("exec finished", get_util(output))

print("place and route #2")
process.stdin.write("create_pblock pblock_arnd1\n")
process.stdin.write("resize_pblock pblock_arnd1 -add {%siiiii}\n" % \
                    s.expand_box(500, 500, 25, 10, {"LUT": 256, "FD": 0, "DSP": 16, "RAMB36": 0, "RAMB18": 0}))
process.stdin.write("add_cells_to_pblock pblock_arnd1 [get_cells [list arnd1]] -clear_locs\n")
process.stdin.write("source tcl/place_and_route.tcl\n")
process.stdin.write("delete_pblock [get_pblocks  pblock_arnd1]\n")
process.stdin.flush()
output = wait_for_complete()
print("exec finished", get_util(output))



print("exiting...")
process.stdin.write("exit\n")
process.stdin.flush()
wait_for_exit()
