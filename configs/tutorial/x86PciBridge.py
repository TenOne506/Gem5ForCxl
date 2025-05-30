import m5
# import all of the SimObjects
from m5.objects import *

# create the system we are going to simulate
system = System()

# Set the clock frequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = "1GHz"
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = "timing"  # Use timing accesses
system.mem_ranges = [AddrRange("512MB")]  # Create an address range

# Create a simple CPU
# You can use ISA-specific CPU models for different workloads:
# `RiscvTimingSimpleCPU`, `ArmTimingSimpleCPU`.
system.cpu =X86TimingSimpleCPU()
# all=dir(system.cpu)
# for a in all:
#     print(a)
# Create a memory bus, a system crossbar, in this case
system.membus = SystemXBar()

# Hook the CPU ports up to the membus
system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# create the interrupt controller for the CPU and connect to the membus
system.cpu.createInterruptController()

# For X86 only we make sure the interrupts care connect to memory.
# Note: these are directly connected to the memory bus and are not cached.
# For other ISA you should remove the following three lines.
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Create a DDR3 memory controller and connect it to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports



# create the PciBridge
# system.pci_host = PciHost()
# system.PciBridge = PciBridge2()
# system.PciBridge.host=PciHost()
# system.PciBridge.DeviceId1=1 
# system.PciBridge.DeviceId2=2
# system.PciBridge.DeviceId3=3 
# system.PciBridge.VendorId =1
# system.PciBridge.sendUpPort
# system.PciBridge.receiveUpPort
# system.PciBridge.sendDownPort1
# system.PciBridge.receiveDownPort1
# system.PciBridge.sendDownPort2
# system.PciBridge.receiveDownPort2
# system.PciBridge.sendDownPort3
# system.PciBridge.receiveDownPort3
# system.PciBridge.sendUpPort = system.membus.cpu_side_ports
# system.PciBridge.receiveUpPort = system.membus.mem_side_ports

# system.pci_host = PciHost()
# use the version2 Pcibridge
system.pcie1 = PCIELink(lanes = 2, speed = 5, mps=5, max_queue_size= 10)
system.pcie2 = PCIELink(lanes = 2 , speed = 5, mps = 5, max_queue_size= 10)
system.pcie3 = PCIELink(lanes = 2 , speed = 5,  mps = 5,max_queue_size= 10)
system.pcie4 = PCIELink(lanes = 2 , speed = 5, mps = 5, max_queue_size= 10)
system.pcie5 = PCIELink(lanes = 2 , speed = 5 ,mps = 5, max_queue_size= 10)
system.pcie6 = PCIELink(lanes = 2 , speed = 5, mps = 5, max_queue_size= 10)

system.hostbridge = PciBridge2()
# system.pcihost=system.hostbridge.host
# all=dir(system.pci_host)
# for a in all:
#     print(a)
# system.platform = Platform()
# # system.realview = system.platform()
# system.pci_host = PcPciHost()
# system.pci_host =system.membus.mem_side_ports
# system.pci_host.request_port = system.membus.cpu_side_ports

system.RootComplex = RootComplex()
system.switch = PCIESwitch()

# system.pci_host = PciHost()

system.RootComplex.host = system.hostbridge.host
system.switch.host = system.hostbridge.host

system.RootComplex.response = system.membus.mem_side_ports
system.RootComplex.request_dma = system.membus.cpu_side_ports

system.RootComplex.response_dma1 = system.pcie1.upstreamRequest
system.RootComplex.response_dma2 = system.pcie2.upstreamRequest
system.RootComplex.response_dma3 = system.pcie3.upstreamRequest 
system.RootComplex.request1    = system.pcie1.upstreamResponse 
system.RootComplex.request2    = system.pcie2.upstreamResponse 
system.RootComplex.request3    = system.pcie3.upstreamResponse 


system.pcie1.downstreamRequest  = system.switch.response
system.pcie1.downstreamResponse = system.switch.request_dma

system.pcie4.downstreamRequest  = system.switch.response_dma1
system.pcie4.downstreamResponse = system.switch.request1
system.pcie5.downstreamRequest  = system.switch.response_dma2
system.pcie5.downstreamResponse = system.switch.request2
system.pcie6.downstreamRequest  = system.switch.response_dma3
system.pcie6.downstreamResponse = system.switch.request3


# try to add Cxl Memory to the system
# system.RootComplex.device1= CxlMemory()
# Here we set the X86 "hello world" binary. With other ISAs you must specify
# workloads compiled to those ISAs. Other "hello world" binaries for other ISAs
# can be found in "tests/test-progs/hello".
# binary = "tests/test-progs/hello/bin/x86/linux/hello"

# system.workload = SEWorkload.init_compatible(binary)

# # Create a process for a simple "Hello World" application
# process = Process()
# # Set the command
# # cmd is a list which begins with the executable (like argv)
# process.cmd = [binary]
# # Set the cpu to use the process as its workload and create thread contexts
# system.cpu.workload = process
# system.cpu.createThreads()
# disk_image = "/path/to/disk/image"
# system.boot_loader = "/path/to/bootloader"
# set up the root SimObject and start the simulation
root = Root(full_system=False, system=system)
# instantiate all of the objects we've created above
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print("Exiting @ tick %i because %s" % (m5.curTick(), exit_event.getCause()))
