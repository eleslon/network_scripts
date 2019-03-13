#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
import netmiko
import re
from tabulate import tabulate
import getpass

username = input('Enter username:')
password = getpass.getpass('Enter password:')

columns = ['Hostname', 'Uptime']
office_switches = {
    's1-Spb-Linx-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.6',
        'username': username,
        'password': password
    },
    's2-Spb-Linx-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.12',
        'username': username,
        'password': password
    },

    's3-Spb-Linx-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.3',
        'username': username,
        'password': password
    },

    's4-Spb-Linx-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.4',
        'username': username,
        'password': password
    }}

switches = {
    'cs1-Spb-Rep-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.2',
        'username': username,
        'password': password
    },
    'cs2-Spb-Rep-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.5',
        'username': username,
        'password': password
    },
    'cs3-Spb-Rep-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.103',
        'username': username,
        'password': password
    },
    's1-Spb-Rep-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.101',
        'username': username,
        'password': password
    },
    's2-Spb-Rep-RU': {
        'device_type': 'cisco_ios',
        'ip': '10.80.109.102',
        'username': username,
        'password': password
    }}


def print_all_data(devices):
    result = []


def get_uptime(*devices):
    result = []
    regex = r'uptime is(.*?)\nSystem'
    for switch in devices:
        for sw in switch:
            temp = []
            try:
                net_connect = ConnectHandler(**switch[sw])
                output = net_connect.send_command('show ver')
                match = re.search(regex, output, re.DOTALL)
                temp.append(sw)
                temp.append(match.groups()[0])
                result.append(tuple(temp))
                print('Getting info from {}'.format(sw) + '   ' + 'OK')
            except (netmiko.ssh_exception.NetMikoAuthenticationException) as error:
                print('Getting info from {}'.format(sw) + '   ' + 'NOT OK')
    if result:
        print('Switches:' + '\n')
        print(tabulate(result, headers=columns))


if __name__ == '__main__':
    get_uptime(office_switches, switches)
