#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
import netmiko
import re
from tabulate import tabulate
import getpass
import yaml
from spb_devices import spb_switches, spb_office_switches, spb_nexuses
from msk_devices import msk_switches, msk_nexuses

username = input('Enter username:')
password = getpass.getpass('Enter password:')
columns = ['Hostname']

def columns_conf(uptime, model, version, memory, cpu, sn):
    if uptime:
        columns.append('Uptime')
    if model:
        columns.append('Model')
    if version:
        columns.append('Version')
    if memory:
        columns.append('Memory(MB)')
    if cpu:
        columns.append('CPU(5s/1m/5m, %)')
    if sn:
        columns.append('Serial Number')
    return columns

def check_config(config_file):
    with open(config_file) as f:
        config = yaml.load(f)
        uptime = config['GET INFO']['Uptime']
        model = config['GET INFO']['Model']
        version = config['GET INFO']['Version']
        memory = config['GET INFO']['Free_memory']
        cpu = config['GET INFO']['CPU']
        sn = config['GET INFO']['SN']
    return uptime, model, version, memory, cpu, sn


def update_auth_info(*args):
    '''
    Функция ожидает аргументы:
    * args - словарь словарей

    Функция меняет значения для ключей 'username' и 'password' на значения, которые были получены от пользователя.
    Возвращает обновленный словарь.
    '''
    for devices in args:
        for device in devices:
            if devices[device]['username'] == None and devices[device]['password'] == None:
                devices[device]['username'] = username
                devices[device]['password'] = password
    return args


def get_data(uptime=False, model=False, version=False, memory=False, cpu=False, sn=False, *args):
    regex = r'uptime is(?P<uptime>.*?)\n'
    regex_version = r'.* +Software.*Version +(?P<version>\S+),|system:    version +(\S+)\n'
    regex_model = r'cisco +(\S+) +Chassis|cisco +(\S+).*processor'
    regex_memory = r'with (?P<memory>\S+)K bytes of memory|with (\S+)K/(\S)K bytes of memory|with (\S+ kB) of memory'
    regex_cpu = r'CPU utilization for five seconds: +(\S+)\/.*one minute: +(\S+); +five minutes: +(\S+)'
    regex_sn = r'PID: N5K-C5548UP       , VID: V01 , SN: (\S+)\n|Processor board ID +(\S+)\n'
    #regex_sn = r'"Nexus5548 Chassis"\nPID: N5K-C5548UP       , VID: V01 , SN: (\S+)\n'
    result = []
    for devices in args:
        for switch in devices:
            print('Getting info from {}'.format(switch), end=" ", flush=True)
            temp = []
            try:
                net_connect = ConnectHandler(**devices[switch])
                temp.append(switch)
                print(' OK')
                if uptime:
                    output = net_connect.send_command('show ver')
                    match = re.search(regex, output, re.DOTALL)
                    temp.append(match.group('uptime'))
                if model:
                    if devices[switch]['device_type'] == 'cisco_nxos':
                        output_model = net_connect.send_command('show ver')
                        match_model = re.search(regex_model, output_model, re.DOTALL)
                        for match in match_model.groups():
                            if match:
                                temp.append(match)
                    if devices[switch]['device_type'] == 'cisco_ios':
                        output_model_ios = net_connect.send_command('show ver | inc processor')
                        match_model_ios = re.search(regex_model, output_model_ios, re.DOTALL)
                        for match in match_model_ios.groups():
                            if match:
                                temp.append(match)

                if version:
                    output_version = net_connect.send_command('show ver')
                    match_version = re.search(regex_version, output_version, re.DOTALL)
                    for match in match_version.groups():
                        if match:
                            temp.append(match)
                if memory:
                    output_memory = net_connect.send_command('sh ver')
                    match_memory = re.search(regex_memory, output_memory, re.DOTALL)

                    for match in match_memory.groups():
                        if match:
                            if '/' in match:
                                backslash = match.find('/')
                                total_memory = int(
                                    round(((int(match[0:backslash - 1]) + int(match[backslash + 1:])) / 1024), 1))
                                temp.append(total_memory)
                            elif ' kB' in match:

                                kB = match.find(' kB')
                                total_memory_nexus = int(
                                    round((int(match[0:kB])) / 1000))
                                temp.append(total_memory_nexus)
                            else:
                                temp.append(round(int(match) / 1024))
                if cpu:
                    output_cpu = net_connect.send_command('sh processes cpu | inc CPU')
                    match_cpu = re.search(regex_cpu, output_cpu, re.DOTALL)
                    cpu = match_cpu.groups()[0] + '/' + match_cpu.groups()[1] + '/' + match_cpu.groups()[2]
                    cpu = cpu.replace('%','')
                    temp.append(cpu)
                if sn:
                    if devices[switch]['device_type'] == 'cisco_nxos':
                        output_sn = net_connect.send_command('sh inventory')
                        match_sn = re.search(regex_sn, output_sn, re.DOTALL)
                        for match in match_sn.groups():
                            if match:
                                temp.append(match)
                    if devices[switch]['device_type'] == 'cisco_ios':
                        output_sn_ios = net_connect.send_command('sh ver')
                        match_sn = re.search(regex_sn, output_sn_ios, re.DOTALL)
                        for match in match_sn.groups():
                            if match:
                                temp.append(match)


                else:
                    pass

                result.append(tuple(temp))


            except (netmiko.ssh_exception.NetMikoAuthenticationException) as error:
                print('    Authentication failed')
            except netmiko.ssh_exception.NetMikoTimeoutException as timeout_error:
                print('    Connection to device timed-out')
            except AttributeError as error:
                print(error)
    if result:
        print('Switches:' + '\n')
        print(tabulate(result, headers=headers))


if __name__ == '__main__':

    devices = update_auth_info(spb_nexuses, spb_switches, spb_office_switches, msk_nexuses, msk_switches)
    #devices = update_auth_info(msk_switches)
    uptime, model, version, memory, cpu, sn = check_config('config.yaml')
    headers = columns_conf(uptime, model, version, memory, cpu, sn)
    get_data(uptime, model, version, memory, cpu, sn, *devices)
