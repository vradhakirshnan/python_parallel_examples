#!env/bin/python

from datetime import datetime, timedelta, date
from dotenv import load_dotenv
import json
import os
import sys
import time
from typing import List, Dict, Type



def get_env(_env_variable:str)-> str:
    '''
    '''
    if _env_variable in os.environ:
        pass
    else:
        load_dotenv('.env')
        if _env_variable in os.environ:
            pass
        else:
            raise Exception(f'Environment Variable {_env_variable} not set')
    return os.environ[_env_variable]


def pretty_print_dict(_dict: Dict):
    '''
    '''
    print('-'*10)
    dict_string = json.dumps(_dict, default=str, indent=4)
    print(f'\n{dict_string}\n')
    print('-'*10)



def continue_program(prompt:str = 'Continue'):
    '''
    '''
    ch = input(prompt + '\n')
    if ch in ['', 'y', 'Y']:
        return
    print('exiting....')
    sys.exit(0)


def load_json_file(_file_name: str)-> Dict:
    '''
    '''
    with open(_file_name, 'r') as f:
        return json.loads(f.read())

def save_json_file(_file_name: str, _dict: Dict, _default: Type = str)-> None:
    '''
    '''
    with open(_file_name, 'w') as f:
        json.dump(_dict, f, default=str, indent=4)
    return




def main():
    print('works')
    continue_program('1')
    continue_program('2')
    continue_program('3')


if __name__ == '__main__':
    main()
