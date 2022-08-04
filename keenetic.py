__author__ = 'Юзов Евгений, ООО "Центр"'

# -*- coding: utf-8 -*-
import requests
from requests.exceptions import HTTPError
from config import ReadConfig
from hashlib import md5, sha256
import json


# Класс реализует CRUD
class Postman:
    session = requests.Session()

    @classmethod
    def get(cls, ip, address, data_to_get=None):
        if data_to_get is None:
            data_to_get = {}
        return cls.session.get(f'http://{ip}{address}', params=data_to_get)

    @classmethod
    def post(cls, ip, address, data_to_post=None):
        if data_to_post is None:
            data_to_post = {}
        return cls.session.post(f'http://{ip}{address}', json=data_to_post)

    @classmethod
    def delete(cls, ip, address):
        return cls.session.delete(f'http://{ip}{address}')


# Основной класс
class Keenetic:
    def __init__(self, auth_host: ReadConfig) -> None:
        login = auth_host.login
        password = auth_host.password
        self.authenticated = self.__auth(auth_host.ip, login, password)

    # Аутентификация на Keenetic
    @staticmethod
    def __auth(ip, login, password):
        response = Postman.get(ip, '/auth')
        if response.status_code == 401:
            realm = response.headers['X-NDM-Realm']
            password = f'{login}:{realm}:{password}'
            password = md5(password.encode('utf-8'))
            challenge = response.headers['X-NDM-Challenge']
            password = challenge + password.hexdigest()
            password = sha256(password.encode('utf-8')).hexdigest()
            try:
                response = Postman.post(ip, '/auth', {'login': login, 'password': password})
                response.raise_for_status()
            except HTTPError as http_error:
                print(f'HTTP error occurred: {http_error}')
                return False
            except Exception as error:
                print(f'Other error occurred: {error}')
                return False
            else:
                return True

    # Выбирает из набора данных значения с определённым ключом, возвращает итератор
    def item_generator(self, json_input, lookup_key: str):
        if isinstance(json_input, dict):
            for k, v in json_input.items():
                if k == lookup_key:
                    yield v
                else:
                    for child_val in self.item_generator(v, lookup_key):
                        yield child_val
        elif isinstance(json_input, list):
            for item in json_input:
                for item_val in self.item_generator(item, lookup_key):
                    yield item_val


if __name__ == '__main__':
    host = ReadConfig('Host1')
    giant = Keenetic(host)

if giant.authenticated:
    try:
        response = Postman.get(host.ip, f'/rci/interface/GigabitEthernet1/vlan{host.vlan_wan}', {})
        response.raise_for_status()
    except HTTPError as http_error:
        print(f'HTTP error occurred: {http_error}')
    except Exception as error:
        print(f'Other error occurred: {error}')
    else:
        print(json.loads(response.text))

    data = {
        'GigabitEthernet0/7': {'rename': '7', 'switchport': {'mode': ['access'], 'access': {'vid': f'{host.vlan_lan}'}},
                               'up': True}, }
    response = Postman.post(host.ip, f'/rci/interface/{list(data.keys())[0]}', data)
    print(json.loads(response.text))

    data = {'GigabitEthernet0/Vlan600': {'rename': 'Testing', 'security-level': {'private': True},
                                         'ip': {'address': {'address': f'{host.ip_lan.split(" ")[0]}',
                                                            'mask': f'{host.ip_lan.split(" ")[1]}'},
                                                'dhcp': {'client': {'hostname': 'Keenetic-8778'}}, 'mtu': '1500'},
                                         'up': True}
            }
    response = Postman.post(host.ip, f'/rci/interface/{list(data.keys())[0]}', data)
    # print(json.loads(response.text))
    for _ in giant.item_generator(json.loads(response.text), 'message'):
        print(_)

    response = Postman.delete(host.ip, '/rci/ip/nat/')
    # print(json.loads(response.text))
    for _ in giant.item_generator(json.loads(response.text), 'message'):
        print(_)

'''
    if giant.authenticated:
        wg_int = json.loads(Postman.post(host.ip, f'/rci/interface/Wireguard{if_num}', {}).text)
        if wg_int != {}:
            print(wg_int['status'][0]['message'])
        answer = json.loads(Postman.post(host.ip, f'/rci/interface/Wireguard{if_num}', data).text)
        print(answer['ip']['address']['status'][0]['message'])
'''
