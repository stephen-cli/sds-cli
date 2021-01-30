"""SDS-CLI - Utility Module

This module contains utility functions for making API requests and
updating a dictionary of information for the usage of the Synology APIs.
"""

from prettytable import prettytable, PrettyTable
import sys
import requests
import errors
import json

apis = {
    'info': {
        'name': 'SYNO.API.Info',
        'version': 1,
        'path': 'query.cgi'
    }
}


def update(api, response, api_name):
    apis.update({
        api: {
            'name': api_name,
            'version': response['data'][api_name]['maxVersion'],
            'path': response['data'][api_name]['path']
        }
    })


def request(address, api, method, params={}, cookies={}):
    api_path = apis.get(api).get('path')

    url = f'http://{address}/webapi/{api_path}'
    params = {
        'api': apis.get(api).get('name'),
        'version': apis.get(api).get('version'),
        'method': method,
        **params
    }

    try:
        response_obj = requests.get(url, params=params, cookies=cookies)

        try:
            response = response_obj.json()

            if not response['success']:
                error_code = response['error']['code']
                errors.handle_error(error_code, api)
                if api == 'auth':
                    errors.handle_auth_error(error_code)
                if api == 'dsTask':
                    errors.handle_ds_task_error(error_code)

            return response
        except json.decoder.JSONDecodeError:
            print('Invalid request URL')
            sys.exit()
    except requests.exceptions.ConnectionError:
        print('Could not connect to provided address')
        sys.exit()


def format_field_names(dict):
    formatted_dict = {}
    for key, value in sorted(dict.items()):
        field_name = key.replace('_', ' ').title()
        formatted_dict[field_name] = value
    return formatted_dict


def tabulate(data):
    if isinstance(data, list):
        all_keys = frozenset().union(*data)
        new_list = [[]]

        for key in sorted(all_keys):
            field_name = key.replace('_', ' ').title()
            new_list[0].append(field_name)

        for object in data:
            for key in all_keys:
                if key not in object:
                    object[key] = {}
            formatted_object = format_field_names(object)
            new_list.append(formatted_object)
        table = prettytable.from_json(json.dumps(new_list))
        return table
    else:
        table = PrettyTable()
        formatted_data = format_field_names(data)
        for key, value in formatted_data.items():
            table.add_column(key, [value])
        return table