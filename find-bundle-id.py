#!/usr/bin/python
# -*- coding: utf-8 -*-
from paramiko import SSHClient, AutoAddPolicy
from bplist import bplist


def write_file(filename, content):
    with open(filename, "w+", encoding="utf-8") as f:
        for line in content:
            f.write(line)
        f.close()


def convert_bplist(data):
    return bplist.BPListReader(data).parse()


def ssh(host, port, username, password):
    app_data = list()
    filename = '.com.apple.mobile_container_manager.metadata.plist'
    dir_path = '/private/var/mobile/Containers/Data/Application/'
    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())
    client.connect(host, port, username, password)
    stdin, stdout, stderr = client.exec_command('ls -l /private/var/mobile/Containers/Data/Application/')
    lines = stdout.readlines()[2:]
    app_list = lines[2:]
    for app_details in app_list:
        app = app_details.split()[-1]
        stdin, stdout, stderr = client.exec_command('cat {0}{1}/{2}'.format(dir_path, app, filename))
        app_data.append((app, convert_bplist(stdout.read())['MCMMetadataIdentifier'].decode()))
    client.close()
    return app_data


def main():
    app_data = ssh(host='192.168.1.15', port=22, username='root', password='alpine')
    app_dump = "Application Data Details\n" \
               "________________________\n" \
               "\nFolder Locations: /private/var/mobile/Containers/Data/Application/\n" \
               "\nFolder Name, Application Bundle ID\n"
    for data in app_data:
        app_dump += '{0}, {1}\n'.format(data[0], data[1])
    write_file('apps.csv', app_dump)


if __name__ == '__main__':
    main()
