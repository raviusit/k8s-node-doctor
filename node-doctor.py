# -*- coding: utf-8 -*-
__author__ = "raviusit@gmail.com"

import os
import sys
import json
import yaml
import socket
import requests
from requests.exceptions import ConnectionError


def main():

    url = "<Slack-webhook-URL>"
    channel = "#Channel-name"

    node_name = os.environ['MY_NODE_NAME']
    cluster_name = os.environ['CLUSTER_NAME']
    slack_enabled = os.environ['SLACK_ENABLED']
    email_enabled = os.environ['EMAIL_ENABLED']
    dc_number = os.environ['DC_NUMBER']

    print('NODE Name is # ' + node_name)
    print('CLUSTER Name is # ' + cluster_name)
    print('Slack Enabled is # ' + slack_enabled)
    print('Email Enabled is # ' + email_enabled)
    print('DataCenter is # ' + dc_number)

    def str2bool(v):
        return v.lower() in ("yes", "true", "t", "1", "True")

    def send_email(message):
        print("### EMAIL section ####")
        pass

    def send_message_slack(message, color):
        """method to send message to Slack
           :param: message (List), color: string
           :return: void
        """
        icon_emoji = ":loudspeaker:"
        title = f"Connectivity Results for Node - {node_name} in {cluster_name}"
        slack_data = {
            "username": str.upper(dc_number) + " " + "Connectivity Notification From Node Doctor",
            "icon_emoji": icon_emoji,
            "channel": channel,
            "attachments": [
                {
                    "color": color,
                    "title": title,
                    "text": message
                }
            ]
        }
        print(json.dumps(slack_data))
        byte_length = str(sys.getsizeof(slack_data))
        headers = {'Content-Type': "application/json", 'Content-Length': byte_length}
        try:
            response = requests.post(url, data=json.dumps(slack_data), headers=headers)
            if response.status_code != 200:
                raise Exception(response.status_code, response.text)
                sys.exit(0)
        except ConnectionError as e:
            print("Exception when posting message to slack: %s\n" % e)
            sys.exit(0)

    def connect(hostname, port, connections_result_passed, connections_result_failed):
        """method to connect to the list of hostnames with ports using socket
        :param: hostname, port
        :param: list successful_connection, failed_connection
        :return:list
        """
        a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        location = (hostname, int(port))
        result_of_check = a_socket.connect_ex(location)
        a_socket.close()
        if result_of_check == 0:
            print("Connectivity for " + hostname + ":" + str(port) + " is Successful!!")
            result = next((True for connections_result_passed in connections_result_passed if hostname in connections_result_passed), False)
            if result:
                result_hostname = [connections_result_passed for connections_result_passed in connections_result_passed
                                   if hostname in connections_result_passed]
                index = connections_result_passed.index(''.join(result_hostname))
                connections_result_passed.append(connections_result_passed[index] + ',' + str(port))
                connections_result_passed.pop(index)
            else:
                connections_result_passed.append(" " + hostname + ":" + str(port))
        else:
            print("Connectivity for " + hostname + ":" + str(port) + " has Failed!!")
            result = next((True for connections_result_failed in connections_result_failed if
                           hostname in connections_result_failed), False)
            if result:
                result_hostname = [connections_result_failed for connections_result_failed in connections_result_failed
                                   if hostname in connections_result_failed]
                index = connections_result_failed.index(''.join(result_hostname))
                connections_result_failed.append(connections_result_failed[index] + ',' + str(port))
                connections_result_failed.pop(index)
            else:
                connections_result_failed.append(" " + hostname + ":" + str(port))
        return connections_result_passed, connections_result_failed

    def construct_message(connections_result, sign):
        block = u'\u258c'
        message_list = []
        for items in connections_result:
                message_list.append('{0}'.format(block))
                message_list.append(' {0} '.format(items))
                message_list.append('{0}'.format(sign))
                message_list.append("\n")
        return message_list

    def message_content(connections_result_passed, connections_result_failed):
        """method to compose the message to be sent on Slack
        :param: List failed_connection
        :return:String
        """
        color = 'good'
        message_list = []
        correct = u'\u2714'
        cross = u'\u2716'

        if len(connections_result_passed + connections_result_failed) == 0:
            message = 'No hosts mentioned in the Endpoints.yaml file'
        else:
            if len(connections_result_failed) > 0:
                color = 'danger'
            failed_content = construct_message(connections_result_failed, cross)
            pass_content = construct_message(connections_result_passed, correct)
            message_list.append("\n")
            message = ''.join(failed_content + pass_content)
            print(message)
        return message, color

    def connection_test():
        """method to test connectivity from the endpoints.yaml file provided as a configmap for each DC
        :param: None
        :return:void
        """
        connections_result_passed = []
        connections_result_failed = []
        with open(f'endpoints/{dc_number}/endpoints.yaml', 'r') as ep_file:
            try:
                yaml_object = yaml.safe_load(ep_file)
                for components in yaml_object.values():
                    for host_info in components.values():
                        if host_info is None:
                            pass
                        else:
                            for hostname, port in host_info.items():
                                if ',' in str(port):
                                    port_list = str(port).split(',')
                                    for items in port_list:
                                        connections_result_passed, connections_result_failed = connect(hostname, items, connections_result_passed, connections_result_failed)
                                else:
                                    connections_result_passed, connections_result_failed = connect(hostname, port, connections_result_passed, connections_result_failed)
                message, color = message_content(connections_result_passed, connections_result_failed)
                if str2bool(slack_enabled) is True and str2bool(email_enabled) is True:
                    send_message_slack(message, color)
                    send_email(message)
                elif str2bool(slack_enabled) is True and str2bool(email_enabled) is False:
                    send_message_slack(message, color)
                elif str2bool(slack_enabled) is False and str2bool(email_enabled) is True:
                    send_email(message)
                else:
                    pass
            except yaml.YAMLError as exc:
                print(exc)

    connection_test()


if __name__ == "__main__":
    main()
