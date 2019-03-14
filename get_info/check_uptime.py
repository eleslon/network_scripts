#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from netmiko import ConnectHandler
import netmiko
import re
from tabulate import tabulate
import getpass
from devices import switches, office_switches

username = input('Enter username:')
password = getpass.getpass('Enter password:')

columns = ['Hostname', 'Uptime']


def get_uptime(*args):
    '''
    Функция ожидает аргументы:
    * args - словарь словарей

    Функция подключается к каждому устройству по SSH из переданного словаря, выполняет "sh ver", парсит uptime
    и выводит информацию на стандартный поток вывода.
    Функция tabulate используется для вывода информации ввиде таблицы.
    Для подключения используется модуль netmiko
    '''
    result = []
    regex = r'uptime is(.*?)\nSystem'
    for devices in args:
        for switch in devices:
            temp = []
            try:
                net_connect = ConnectHandler(**devices[switch])
                output = net_connect.send_command('show ver')
                match = re.search(regex, output, re.DOTALL)
                temp.append(switch)
                temp.append(match.groups()[0])
                result.append(tuple(temp))
                print('Getting info from {}'.format(switch) + '   ' + 'OK')
            except (netmiko.ssh_exception.NetMikoAuthenticationException) as error:
                print('Getting info from {}'.format(switch) + '   ' + 'NOT OK')
    if result:
        print('Switches:' + '\n')
        print(tabulate(result, headers=columns))


if __name__ == '__main__':
    get_uptime(office_switches, switches)
