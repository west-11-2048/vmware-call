# main.py
import argparse
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim, vmodl
import ssl

def get_vmware_hosts_and_images(vcenter, user, password):
    try:
        # Disable SSL certificate verification
        context = ssl._create_unverified_context()
        
        # Connect to vCenter server
        si = SmartConnect(host=vcenter, user=user, pwd=password, sslContext=context)
        
        # Retrieve the content
        content = si.RetrieveContent()
        
        # Get all the hosts
        host_view = content.viewManager.CreateContainerView(content.rootFolder, [vim.HostSystem], True)
        hosts = host_view.view
        
        host_info = []
        
        for host in hosts:
            host_name = host.name
            running_vms = []
            stopped_vms = []
            
            for vm in host.vm:
                vm_info = {
                    'name': vm.name,
                    'memory': vm.config.hardware.memoryMB,
                    'cpu': vm.config.hardware.numCPU
                }
                if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                    running_vms.append(vm_info)
                else:
                    stopped_vms.append(vm_info)
            
            host_info.append({
                'host_name': host_name,
                'running_vms': running_vms,
                'stopped_vms': stopped_vms
            })
        
        Disconnect(si)
        return host_info
    
    except vmodl.MethodFault as error:
        print(f"Caught vmodl fault: {error.msg}")
    except Exception as e:
        print(f"Caught exception: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="HelloWorld Command Line Interface")
    
    print("Adding 'call' command")
    parser.add_argument('--call', nargs=3, metavar=('vcenter', 'user', 'password'),
                        help='Call with three parameters')
    
    # Adding 'reset' command
    parser.add_argument('--reset', nargs=2, metavar=('param1', 'param2'),
                        help='Reset with two parameters')
    
    args = parser.parse_args()
    print(args)
    
    if args.call:
        vcenter, user, password = args.call
        host_info = get_vmware_hosts_and_images(vcenter, user, password)
        if host_info:
            for host in host_info:
                print(f"Host: {host['host_name']}")
                print("  Running VMs:")
                print(f"{'Name':<20} {'Memory (MB)':<15} {'CPU (vCPUs)':<10}")
                for vm in host['running_vms']:
                    print(f"{vm['name']:<20} {vm['memory']:<15} {vm['cpu']:<10}")
                print("  Stopped VMs:")
                print(f"{'Name':<20} {'Memory (MB)':<15} {'CPU (vCPUs)':<10}")
                for vm in host['stopped_vms']:
                    print(f"{vm['name']:<20} {vm['memory']:<15} {vm['cpu']:<10}")
    
    if args.reset:
        param1, param2 = args.reset
        print(f"Reset command received with parameters: {param1}, {param2}")

if __name__ == "__main__":
    main()