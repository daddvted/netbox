from XenAPI import Session

def sync_xen(host: str, username: str, password: str) -> list:
    try:
        session = Session(f'http://{host}/')
        session.login_with_password(username, password, '1.0', 'xen-api-scripts-xenapi.py')
        all = session.xenapi.VM.get_all()

        vms = []
        for vm in all:
            record = session.xenapi.VM.get_record(vm)
            if not(record["is_a_template"]) and not(record["is_control_domain"]):
                info = {
                    'name': record["name_label"],
                    'status': "active" if record["power_state"] == "Running" else "offline",
                    # 'vcpus': vm["cpu_no"],
                    # 'memory': vm["memory"],
                }
                vms.append(info)
        return vms
    except Exception as err:
        print(f"[sync_xen]: {err}")

    finally:
        try:
            session.xenapi.session.logout()
        except AttributeError as err:
            print(f"[sync_xen]: {err}")
            return []
