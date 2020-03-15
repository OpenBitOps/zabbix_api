#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/3/15 14:06
# @Author  : Ethan
# @File    : config_get.py

import yaml
import io
import os


def config():
    """
    Get the username / password / URL of the API in the configuration file config
    :return: username, password, api_url
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(base_dir, 'zabbix_config.yml')

    f = io.open(yaml_path, 'rb')
    conf_ = yaml.load(f, Loader=yaml.FullLoader)
    username = conf_['authentication']['user']
    password = conf_['authentication']['password']
    api_url = conf_['urls']['zabbix_api_url']
    log_file = conf_['logs']['result_log']
    f.close()

    return username, password, api_url, log_file
