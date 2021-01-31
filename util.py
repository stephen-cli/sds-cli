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
    """Update the list of known Synology APIs

    The first parameter should be the key that will be used to refer to
    the API when making requests

    The second parmeter should be the response received from the
    DiskStation Info API

    The third paremeter should be the actual name of the API as it is
    recognised by the DiskStation endpoints
    """
    apis.update({
        api: {
            'name': api_name,
            'version': response['data'][api_name]['maxVersion'],
            'path': response['data'][api_name]['path']
        }
    })


def request(address, api, method, params={}, cookies={}):
    """Makes a request to the DiskStation API"""
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


def tabulate_dictionary(data, filter):
    all_keys = frozenset().union(*data)
    new_list = [[]]

    # Determine if results can/should be filtered
    filter_results = False
    if filter:
        if filter[0].replace(' ', '_').lower() in all_keys:
            filter_results = True
        else:
            key = filter[0].replace('_', ' ').title()
            print(f'[{key}] isn\'t a column')

    # Assign the first index of the list to a list of the columns
    for key in sorted(all_keys):
        field_name = key.replace('_', ' ').title()
        new_list[0].append(field_name)

    # Populate the list with rows
    for object in data:
        for key in all_keys:
            if key not in object:
                object[key] = {}
        formatted_object = format_field_names(object)

        if filter_results:
            filter_key = filter[0].replace('_', ' ').title()
            filter_val = filter[1]
            if filter_val in str(formatted_object[filter_key]):
                new_list.append(formatted_object)
        else:
            new_list.append(formatted_object)

    return prettytable.from_json(json.dumps(new_list))


def tabulate_list(data):
    table = PrettyTable()
    formatted_data = format_field_names(data)
    for key, value in formatted_data.items():
        table.add_column(key, [value])
    return table


def tabulate(data, filter={}):
    """Returns a table representing the passed data

    Can take a list of dictionaries for a multirow table or a single
    dictionary for a singlerow table

    A filter parameter can be provided - this should contain a column to
    filter by, and the value to find in the column. Filters are ignored
    when passed a dict instead of a list
    """
    if isinstance(data, list):
        return tabulate_dictionary(data, filter)
    else:
        return tabulate_list(data)
