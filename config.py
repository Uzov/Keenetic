__author__ = 'Юзов Евгений, ООО "Центр"'

import configparser

CONFIG_FILE_NAME = "keenetic.conf"


class ReadConfig:
    def __init__(self, host) -> None:
        '''self.description = self.__get_settings('Wireguard', 'description')
        self.tunnel_ip = self.__get_settings('Wireguard', 'tunnel_ip')
        self.access_group = self.__get_settings('Wireguard', 'access_group')
        self.listen_port = self.__get_settings('Wireguard', 'listen_port')
        self.peer_public_key = self.__get_settings('Wireguard', 'peer_public_key')
        self.server_ip = self.__get_settings('Wireguard', 'server_ip')
        self.allow_ips = list(self.__get_settings('Wireguard', 'allow_ips').split(','))'''
        self.ip = self.__get_settings(host, 'ip')
        self.login = self.__get_settings(host, 'login')
        self.password = self.__get_settings(host, 'password')
        self.ip_lan = self.__get_settings(host, 'ip_lan')
        self.ip_wan = self.__get_settings(host, 'ip_wan')
        self.vlan_lan = self.__get_settings(host, 'vlan_lan')
        self.vlan_wan = self.__get_settings(host, 'vlan_wan')

    @staticmethod
    def __get_settings(section, settings) -> str:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_NAME)
        value = config.get(section, settings)
        return value
