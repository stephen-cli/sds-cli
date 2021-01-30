"""SDS-CLI - Errors Module

The functions in this module are useful for reporting descriptive error
messages back to the user.
"""

import sys


def handle_error(code, api):
    if api == 'dsInfo':
        full_api_name = 'Disk Station Info'
    if api == 'dsTask':
        full_api_name = 'Disk Station Task'
    else:
        full_api_name = api.title()
    if api:
        print(f'Error in {full_api_name} request')

    if code == 100:
        print('Unknown error')
    elif code == 101:
        print('Invalid parameter')
    elif code == 102:
        print('The requested API does not exist')
    elif code == 103:
        print('The requested method does not exist')
    elif code == 104:
        print('The requested version does not support the functionality')
    elif code == 105:
        print('The logged in session does not have permission')
    elif code == 106:
        print('Session timeout')
    elif code == 107:
        print('Session interrupted by duplicate login')


def handle_auth_error(code):
    if code == 400:
        print('No such account or incorrect password')
    elif code == 401:
        print('Account disabled')
    elif code == 402:
        print('Permission denied')
    elif code == 403:
        print('2-step verification code required')
    elif code == 404:
        print('Failed to authenticate 2-step verification code')
    sys.exit()


def handle_ds_task_error(code):
    if code == 400:
        print('File upload failed')
    elif code == 401:
        print('Max number of tasks reached')
    elif code == 402:
        print('Destination denied')
    elif code == 403:
        print('Destination does not exist')
    elif code == 404:
        print('Invalid task id')
    elif code == 405:
        print('Invalid task action')
    elif code == 406:
        print('No default destination')
    elif code == 407:
        print('Set destination failed')
    elif code == 408:
        print('File does not exist')
    sys.exit()
