#!/usr/bin/env python3

"""Synology DiskStation CLI Tool

A CLI that can be used to interact with a Synology NAS on your network.
Synology APIs used:
- Base API
- Synology Download Station API
"""

from getpass import getpass
import util
import errors
import argparse


def get_args():
    parser = argparse.ArgumentParser(description='DiskStation CLI')
    parser.add_argument('address', help=('Server address with IP/domain name'
                                         'and port (e.g. myds.com:5000)'))

    parser.add_argument('--username', '-u',
                        help='User to log in as',
                        metavar='<username>')

    parser.add_argument('--verbose', '-v',
                        action=argparse.BooleanOptionalAction,
                        help='Verbose error logging')

    subparsers = parser.add_subparsers(title='commands',
                                       dest='command',
                                       required=True)

    subparsers.add_parser('info', help='Returns Download Station info')

    subparsers.add_parser('get-config', help='Returns Download Station config')

    parser_gt = subparsers.add_parser('get-tasks',
                                      help=('Provides task listing and '
                                            'detailed task information'))
    parser_gt.add_argument('--id', '-i',
                           type=str,
                           help=('Task IDs, separated by ",". Cannot be used '
                                 'with --offset or --limit.'),
                           metavar='<id>')
    parser_gt.add_argument('--detail', '-d',
                           action=argparse.BooleanOptionalAction)
    parser_gt.add_argument('--transfer', '-t',
                           action=argparse.BooleanOptionalAction)
    parser_gt.add_argument('--offset', '-o',
                           type=int,
                           help=('Beginning task on the request record. '
                                 'Default to "0". Ignored when --id is '
                                 'passed.'),
                           metavar='<offset>')
    parser_gt.add_argument('--limit', '-l',
                           type=int,
                           help=('Number of records requested. Default to '
                                 'list all tasks. Ignored when --id is '
                                 'passed.'),
                           metavar='<limit>')
    parser_gt.add_argument('--filter', '-f',
                           nargs=2,
                           type=str,
                           help=('Displays results where the passed value is '
                                 'found in the given field. Ignored when --id '
                                 'is passed.\n(Note: --filter is applied '
                                 'AFTER --offset and --limit)'),
                           metavar=('<field>', '<value>'))
    parser_gt.add_argument('--sort', '-s',
                           nargs=2,
                           type=str,
                           help=('Orders rows according to the values of the '
                                 'specified column. Ignored when --id is '
                                 'passed.'),
                           metavar=('<field>', '[desc|asc]'))

    return parser.parse_args()


def main():
    args = get_args()
    errors.verbose = args.verbose
    address = args.address

    api_info_params = {
        'query': ('SYNO.API.Auth,'
                  'SYNO.DownloadStation.Info,'
                  'SYNO.DownloadStation.Task')
    }
    api_info = util.request(address, 'info', 'query', api_info_params)

    util.update('auth', api_info, 'SYNO.API.Auth')
    util.update('dsInfo', api_info, 'SYNO.DownloadStation.Info')
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

    if args.command == 'info':
        info = util.request(address, 'dsInfo', 'getinfo', {}, {'id': sid})
        info_table = util.tabulate(info['data'])
        print(info_table)
    if args.command == 'get-config':
        config = util.request(address, 'dsInfo', 'getconfig', {}, {'id': sid})
        config_table = util.tabulate(config['data'])
        print(config_table)
    if args.command == 'get-tasks':
        task_info_params = {
            'id': args.id,
            'additional': ''
        }
        if args.detail:
            task_info_params['additional'] += 'detail,'
        if args.transfer:
            task_info_params['additional'] += 'transfer,'

        if args.id:
            task_info = util.request(address, 'dsTask', 'getinfo',
                                     task_info_params, {'id': sid})
            task_info_table = util.tabulate(task_info['data']['tasks'])
            print(task_info_table)
        else:
            if args.offset:
                task_info_params['offset'] = args.offset
            if args.limit:
                task_info_params['limit'] = args.limit

            task_list = util.request(address, 'dsTask', 'list',
                                     task_info_params, {'id': sid})
            task_list_table = util.tabulate(task_list['data']['tasks'],
                                            args.filter)

            if args.sort:
                column = args.sort[0].replace('_', ' ').title()
                sort = args.sort[1]
                if sort != 'desc' and sort != 'asc':
                    print((f'[{sort}] isn\'t a valid sort option. Specify '
                           '[desc] or [asc]'))
                else:
                    task_list_table.reversesort = sort == 'desc'
                    try:
                        task_list_table.sortby = column
                    except Exception:
                        print(f'[{column}] isn\'t a column')

            print(task_list_table)

    util.request(address, 'auth', 'logout',  {'session': 'DownloadStation'})


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
