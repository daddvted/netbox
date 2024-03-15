from .util import run_remote_command


def sync_kvm(host, username, password, port="22"):
    vms = []
    cmds = [
        "virsh list --state-running --name", 
        "virsh list --all --name",
    ]
    result = run_remote_command(host, port, username, password, cmds)
    print(f"[sync_kvm]: {result}")
    if len(result) == 2:
        running_vms = result[0]["stdout"].split("\n")
        all_vms = result[1]["stdout"].split("\n")
        offline_vms = list(set(all_vms) - set(running_vms))

        print(running_vms, offline_vms)
        for vm in running_vms:
            info = {
                "name": vm,
                "status": "active",
            }
            vms.append(info)
        
        for vm in offline_vms:
            info = {
                "name": vm,
                "status": "offline",
            }
            vms.append(info)

        return vms
    else:
        return vms
