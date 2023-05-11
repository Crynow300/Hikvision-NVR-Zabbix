import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPDigestAuth
from pyzabbix import ZabbixMetric, ZabbixSender
import argparse

parser = argparse.ArgumentParser(description='Скрипт мониторинга Hi-Watch NVR и отправки метрик в Zabbix')

# Add Arguments
parser.add_argument('ip_addr', type=str, help='IP-адрес')
parser.add_argument('hostname', type=str, help='Имя хоста')

# Parse Arguments
args = parser.parse_args()

# Assigning Argument Values to Variables
ip_addr = args.ip_addr
hostname = args.hostname


#Auth String
username = 'admin'
password = 'Pivtochk@2023'
auth = HTTPDigestAuth(username, password)

#Items ISAPI URL`s
URL_hdd = f'http://{ip_addr}/ISAPI/ContentMgmt/Storage/hdd/'
URL_chan1 = f'http://{ip_addr}/ISAPI/ContentMgmt/InputProxy/channels/1/status'
URL_chan2 = f'http://{ip_addr}/ISAPI/ContentMgmt/InputProxy/channels/2/status'
URL_chan3 = f'http://{ip_addr}/ISAPI/ContentMgmt/InputProxy/channels/3/status'
URL_chan4 = f'http://{ip_addr}/ISAPI/ContentMgmt/InputProxy/channels/4/status'

#Requests
response_hdd = requests.get(URL_hdd, auth=auth)
response_chan1 = requests.get(URL_chan1, auth=auth)
response_chan2 = requests.get(URL_chan2, auth=auth)
response_chan3 = requests.get(URL_chan3, auth=auth)
response_chan4 = requests.get(URL_chan4, auth=auth)

#Search in XML
root_hdd = ET.fromstring(response_hdd.text)
status = root_hdd.find('.//{http://www.hikvision.com/ver20/XMLSchema}status')
capacity = root_hdd.find('.//{http://www.hikvision.com/ver20/XMLSchema}capacity')
free = root_hdd.find('.//{http://www.hikvision.com/ver20/XMLSchema}freeSpace')

root_chan1 = ET.fromstring(response_chan1.text)
status_chan1 = root_chan1.find('.//{http://www.hikvision.com/ver20/XMLSchema}online')

root_chan2 = ET.fromstring(response_chan2.text)
status_chan2 = root_chan2.find('.//{http://www.hikvision.com/ver20/XMLSchema}online')

root_chan3 = ET.fromstring(response_chan3.text)
status_chan3 = root_chan3.find('.//{http://www.hikvision.com/ver20/XMLSchema}online')

root_chan4 = ET.fromstring(response_chan4.text)
status_chan4 = root_chan4.find('.//{http://www.hikvision.com/ver20/XMLSchema}online')

#Numerical conversions
capacity_int = int(capacity.text)
free_int = int(free.text)
capacity_gb = round(capacity_int / 1024)
free_gb = round(free_int / 1014)


print("HDD Status:", status.text)
print("HDD Capacity:", capacity_gb, "Gb")
print("HDD Free Space:", free_gb, "Gb")
if status_chan1 is None:
    status_chan1 = 'false'
    print("Channel 1 Status:", status_chan1)
else:
    print("Channel 1 Status:", status_chan1.text)
if status_chan2 is None:
    status_chan2 = 'false'
    print("Channel 2 Status:", status_chan2)
else:
    print("Channel 2 Status:", status_chan2.text)
if status_chan3 is None:
    status_chan3 = 'false'
    print("Channel 3 Status:", status_chan3)
else:
    print("Channel 3 Status:", status_chan3.text)
if status_chan4 is None:
    status_chan4 = 'false'
    print("Channel 4 Status:", status_chan4)
else:
    print("Channel 4 Status:", status_chan4.text)


#Send Metrics to Zabbix
zabbix_sender = ZabbixSender(zabbix_server='zabbix.pivtochka.com')
metrics = [
    ZabbixMetric(f'{hostname}', 'nvr.hdd.status', status.text),
    ZabbixMetric(f'{hostname}', 'nvr.hdd.capacity', str(capacity_gb)),
    ZabbixMetric(f'{hostname}', 'nvr.hdd.free.space', str(free_gb)),
    ZabbixMetric(f'{hostname}', 'nvr.chan1.status', str(status_chan1) if status_chan1 is None else (status_chan1 if isinstance(status_chan1, str) else str(status_chan1.text))),
    ZabbixMetric(f'{hostname}', 'nvr.chan2.status', str(status_chan2) if status_chan2 is None else (status_chan2 if isinstance(status_chan2, str) else str(status_chan2.text))),
    ZabbixMetric(f'{hostname}', 'nvr.chan3.status', str(status_chan3) if status_chan3 is None else (status_chan3 if isinstance(status_chan3, str) else str(status_chan3.text))),
    ZabbixMetric(f'{hostname}', 'nvr.chan4.status', str(status_chan4) if status_chan4 is None else (status_chan4 if isinstance(status_chan4, str) else str(status_chan4.text))),
]

result = zabbix_sender.send(metrics)

print(result)
