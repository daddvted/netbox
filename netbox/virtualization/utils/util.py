import re
import math
from difflib import SequenceMatcher
import paramiko

def extract_sn(sn: str) -> str:
    """
    Extract serial number from sn string, which has the format below:
    '|----Serial Number............................................J301C86M'

    :param sn: String contains serial number
    :return: Serial number(i.e. J301C86M)
    """
    return sn.split('.')[-1]


def convert_power_state(text:str="") -> int:
    state_text = text.lower()

    if state_text == 'poweredon':
        return 0
    if state_text == 'poweredoff':
        return 1
    if state_text == 'suspended':
        return 2


def extract_ip(text="") -> str:
    regex = r"(((25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?))"
    m = re.search(regex, text)
    if m:
        return m.group(0)
    else:
        # return "NO_IP_IN_NAME"
        return "127.0.0.1"


def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def sort_by_dict_value(l: list) -> list:
    return sorted(l, key=lambda x: x['name'])


def get_auth_from_comments(comments: str) -> tuple:
    l = comments.split(',')
    if len(l) == 2:
        return l[0], l[1]
    else:
        return "", ""
    

def get_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def run_remote_command(host, port, username, password, cmds: list, ) -> list:
    """
    Run remote command

    :param host:
    :param port:
    :param username:
    :param password:
    :param cmds:
    :return: A tuple with 'host' as 0st element, and 2nd element for result of every command in 'cmds' as value(list)
    [
        {
            "cmd": "command",
            "stdout": "hello",
            "stderr": "error,
        }
        ...
    ]
    """

    result = []
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, port=port, username=username, password=password)

        for cmd in cmds:
            info = {
                'cmd': cmd
            }
            _, stdout, stderr = client.exec_command(cmd)
            if stdout:
                info['stdout'] = stdout.read().decode().strip()
            if stderr:
                info['stderr'] = stderr.read().decode().strip()
            result.append(info)
        return result
    except Exception as err:
        print(f"[run_remote_command]:{err}")
        return result