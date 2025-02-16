from django.core.management.base import BaseCommand, CommandError, CommandParser
from virtualization.utils.util import get_auth_from_comments, extract_ip
from virtualization.models import VirtualMachine
from virtualization.models import Cluster
from dcim.models import Device



class Command(BaseCommand):
    help = '同步虚拟化群集中的虚拟机'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('--list', action='store_true', dest='list', help='列出当前虚拟机群集')
        parser.add_argument('--clusters', nargs='+', dest='clusters', help='指定要同步的群集名')

    def print_msg(self, msg: str, level:str=""):
        if level == "success":
            self.stdout.write(self.style.SUCCESS(msg))
        elif level == "warning":
            self.stdout.write(self.style.WARNING(msg))
        elif level == "error":
            self.stdout.write(self.style.ERROR(msg))
        else:
            self.stdout.write(self.style.NOTICE(msg))

    def sync_cluster(self, clusters: list):
        for cluster in Cluster.objects.filter(name__in=clusters):
            cluster_type = cluster.type.name.lower()
            device_count = cluster.devices.count()
            self.print_msg(f"🐛 Found {device_count} devices in cluster({cluster})")

            if device_count == 0:
                self.print_msg(f"{cluster.name} 群集中未找到设备", "warning")
                continue

            for device in cluster.devices.all():
                if not device.name:
                    self.print_msg(f"IP address not found in device name for device({device}) in cluster({cluster}), skip", "warning")
                    continue

                device_ip = extract_ip(device.name)

                # Get authentication from comments of cluster
                # Format:
                #   username: xxxxxx
                #   password: yyyyyy
                username, password = get_auth_from_comments(device.comments)
                if not username or not password:
                    self.print_msg(f" Username or password not found in comments of device({device}) in cluster({cluster}), skip", "error")
                    continue

                self.print_msg(f"🐛 Sync VMs for device({device}) in cluster {cluster}")

                if cluster_type == "vmware":
                    vms = sync_vmware(device_ip, username, password)
                elif cluster_type == "xen":
                    vms = sync_xen(device_ip, username, password)
                elif cluster_type == "kvm":
                    vms = sync_kvm(device_ip, username, password)

                for vm in vms:
                    vm_in_db = VirtualMachine.objects.filter(cluster=cluster, name__contains=vm['name'])
                    if vm_in_db.count() == 0:
                        self.print_msg(f"VM({vm['name']} not found in DB, adding")

                        ip = extract_ip(vm['name'])

                        ipaddr = IPAddress()
                        ipaddr.address = ip
                        ipaddr.save()


                        vm_instance = VirtualMachine()
                        vm_instance.name = vm['name']
                        vm_instance.status = vm['status']
                        vm_instance.primary_ip4 = ipaddr
                        if vm.get('vcpus', 0):
                            vm_instance.vcpus = vm['vcpus']
                        if vm.get('memory', 0):
                            vm_instance.memory = vm['memory']
                        vm_instance.cluster = cluster
                        # Bind vm to device(physical machine)
                        vm_instance.device = device
                        vm_instance.save()

                    else:
                        self.print_msg(f"🐛 Found {vm_in_db.count()} VMs in DB by search: {vm['name']}, skip", "warning")

    def handle(self, *args, **options):
        print(f"args: {args}")
        print(f"options: {options}")
        print(options.values())
        print(any(options.values()))

        # 排除 verbosity，检查是否有自定义参数被提供
        custom_options = {k: v for k, v in options.items() if k not in ['verbosity', 'settings', 'pythonpath']}
        if not any(custom_options.values()):
            self.print_help('manage.py', 'sync_inspur')
            return


        if options["list"]:
            self.stdout.write(self.style.SUCCESS("Current Clusters:"))
            clusters = Cluster.objects.all()
            for cluster in clusters:
                print(f"{cluster}")
        elif options['clusters']:
            clusters = options['clusters']
            self.sync_cluster(clusters)
            # self.stdout.write(self.style.SUCCESS(f'Syncing data for clusters: {", ".join(clusters)}'))


        self.stdout.write(self.style.SUCCESS("Done"))