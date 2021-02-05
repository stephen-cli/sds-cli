#!/usr/bin/env python3

"""Synology DiskStation CLI Tool

A CLI that can be used to interact with a Synology NAS on your network.
Synology APIs used:
- Base API
- Synology Download Station API
"""

from getpass import getpass
import sys
import argparse
import util
import errors


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
    parser.add_argument('--human-readable', '-H',
                        action=argparse.BooleanOptionalAction,
                        help=('Print sizes like 1 KB, 234 MB, 2 GB etc. and '
                              'timestamps like 5 hours 54 minutes 1 second'))

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

    parser_ct = subparsers.add_parser('create-task',
                                      help=('Creates a task'))
    parser_ct.add_argument('--uri', '-U',
                           type=str,
                           help=('Accepts HTTP/FTP/magnet/ED2K links or the '
                                 'file path starting with a shared folder, '
                                 'separated by ","'),
                           metavar='<address>')
    # parser_ct.add_argument('--file', '-f',
    #                        type=str,
    #                        help='File uploading from client',
    #                        metavar='<file>')
    parser_ct.add_argument('--username', '-u',
                           type=str,
                           help='Login username',
                           metavar='<username>')
    parser_ct.add_argument('--password', '-p',
                           type=str,
                           help='Login password',
                           metavar='<password>')
    parser_ct.add_argument('--unzip-password', '-z',
                           type=str,
                           help='Password for unzipping download tasks',
                           metavar='<unzip_password>')
    parser_ct.add_argument('--destination', '-d',
                           type=str,
                           help=('Download destination path starting with a '
                                 'shared folder'),
                           metavar='<destination>')

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
    elif args.command == 'get-config':
        config = util.request(address, 'dsInfo', 'getconfig', {}, {'id': sid})
        config_table = util.tabulate(config['data'])
        print(config_table)
    elif args.command == 'get-tasks':
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

            if args.human_readable:
                size = task_info['data']['tasks']['size']
                size = util.readable_storage(size)
                task_info['data']['tasks']['size'] = size

            task_info_table = util.tabulate(task_info['data']['tasks'])
            print(task_info_table)
        else:
            if args.offset:
                task_info_params['offset'] = args.offset
            if args.limit:
                task_info_params['limit'] = args.limit

            task_list = util.request(address, 'dsTask', 'list',
                                     task_info_params, {'id': sid})

            if args.human_readable:
                for task in task_list['data']['tasks']:
                    task['size'] = util.readable_storage(task['size'])

            if args.detail or args.transfer:
                tasks = util.get_additional_columns(task_list['data']['tasks'],
                                                    args)
                task_list_table = util.tabulate(tasks, args.filter)
            else:
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
    elif args.command == 'create-task':
        params = {}
        if args.uri:
            params['uri'] = args.uri
        # elif args.file:
        #     params['file'] = args.file
        else:
            # print('specify uri or file')
            print('specify uri')
            sys.exit()
        if args.username:
            params['username'] = args.username
        if args.password:
            params['password'] = args.password
        if args.unzip_password:
            params['unzip_password'] = args.unzip_password
        if args.destination:
            params['destination'] = args.destination

        util.request(address, 'dsTask', 'create', params, {'id': sid})

    util.request(address, 'auth', 'logout',  {'session': 'DownloadStation'})


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
