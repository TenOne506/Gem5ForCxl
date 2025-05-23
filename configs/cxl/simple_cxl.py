# Copyright (c) 2017 Jason Lowe-Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

""" This file creates a barebones system and executes 'hello', a simple Hello
World application. Adds a simple cache between the CPU and the membus. Using CXLSwitch.

This config file assumes that the x86 ISA was built.
"""

# import the m5 (gem5) library created when gem5 is built
import m5

# import all of the SimObjects
from m5.objects import *
from caches import *
# create the system we are going to simulate
system = System()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "2GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("16MB"),AddrRange("16MB","32MB"),AddrRange("32MB","48MB")]  # Create an address range

# Create a simple CPU
system.cpu = X86TimingSimpleCPU()

# # Create an L1 instruction and data cache
# system.cpu.icache = L1ICache()
# system.cpu.dcache = L1DCache()

# # Connect the instruction and data caches to the CPU
# system.cpu.icache.connectCPU(system.cpu)
# system.cpu.dcache.connectCPU(system.cpu)

# # Create a memory bus, a coherent crossbar, in this case
# system.l2bus = L2XBar()

# # Hook the CPU ports up to the l2bus
# system.cpu.icache.connectBus(system.l2bus)
# system.cpu.dcache.connectBus(system.l2bus)

# # Create an L2 cache and connect it to the l2bus
# system.l2cache = L2Cache()
# system.l2cache.connectCPUSideBus(system.l2bus)

# Create a memory bus
system.membus = SystemXBar()

system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# # Connect the L2 cache to the membus
# system.l2cache.connectMemSideBus(system.membus)

# create the interrupt controller for the CPU and connect to the membus
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

#create the WAL module
system.journal = WALJournal(latency=100)
system.journal.cpu_side_port = system.membus.mem_side_ports


# create the CXLSwitch
system.cxlswitch = CXLSwitch(latency=100)
system.cxlswitch.cpu_side_port = system.journal.mem_side_port

# Create a DDR3 memory controller and connect it to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8(device_size="1MB")
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.cxlswitch.mem_side_port


# create another CXLSwitch
system.cxlswitch2 = CXLSwitch(latency=100)
system.cxlswitch2.cpu_side_port = system.cxlswitch.switch_side_port


system.mem_ctrl2 = MemCtrl()
system.mem_ctrl2.dram = DDR3_1600_8x8(device_size="1MB")
system.mem_ctrl2.dram.range = system.mem_ranges[1]
system.mem_ctrl2.port = system.cxlswitch2.mem_side_port

system.mem_ctrl3 = MemCtrl()
system.mem_ctrl3.dram = DDR3_1600_8x8(device_size="1MB")
system.mem_ctrl3.dram.range = system.mem_ranges[2]
system.mem_ctrl3.port = system.cxlswitch2.switch_side_port


# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# Create a process for a simple "Hello World" application
process = Process()
# Set the command
# grab the specific path to the binary
thispath = os.path.dirname(os.path.realpath(__file__))
binpath = os.path.join(
    thispath, "../../", "tests/test-progs/hello/bin/x86/linux/hello"
)
# binpath = "/home/bill/Desktop/lab/test/hash/hashTest"
# binpath = "/home/bill/Desktop/lab/test/Array/ArrayTest"
# binpath = "/home/bill/Desktop/lab/test/RedBlackTest/RedBlackTest"
# binpath = "/home/bill/Desktop/lab/test/Bpp/Bpptest"
# cmd is a list which begins with the executable (like argv)
process.cmd = [binpath]
# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

system.workload = SEWorkload.init_compatible(binpath)

# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print(f"Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
