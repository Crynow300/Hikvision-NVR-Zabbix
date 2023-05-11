import os

with open('NVR.txt') as f:
    for line in f:
        ip_addr, hostname = line.strip().split()
        os.system(f'python3 hikvision-isapi-test.py {ip_addr} {hostname}')
