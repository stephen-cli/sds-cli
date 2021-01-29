#!/usr/bin/env python3

"""Synology DiskStation CLI Tool

A CLI that can be used to interact with a Synology NAS on your network.
Synology APIs used:
- Base API
- Synology Download Station API
"""

from getpass import getpass
import util
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='DiskStation CLI')
    parser.add_argument('address',
                        help='Server address with IP/domain name and port \
                            (e.g. myds.com:5000)')
    parser.add_argument('-u', '--username',
                        help='User to log in as')

    return parser.parse_args()


def main():
    args = get_args()
    address = args.address

    api_info_params = {'query': 'SYNO.API.Auth,SYNO.DownloadStation.Task'}
    api_info = util.request(address, 'info', 'query', api_info_params)

    util.update('auth', api_info, 'SYNO.API.Auth')
    util.update('dsTask', api_info, 'SYNO.DownloadStation.Task')

    if args.username:
        username = args.username
    else:
        username = input('Username: ')

    password = getpass()

    login_params = {
        'account': username,
        'passwd': password,
        'session': 'DownloadStation',
        'format': 'sid'
    }
    login = util.request(address, 'auth', 'login', login_params)

    sid = login['data']['sid']

    list = util.request(address, 'dsTask', 'list', {}, {'id': sid})

    print(list)

    util.request(address, 'auth', 'logout',  {'session': 'DownloadStation'})


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
