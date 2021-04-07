import json
import os
import socket
import urllib

import requests

TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY", None)
RECEIVER_ID = os.environ.get("RECEIVER_ID", None)
REMOTE_API_SERVER_URL = os.environ.get("REMOTE_API_SERVER_URL", None)
REMOTE_API_SERVER_KEY = os.environ.get("REMOTE_API_SERVER_KEY", None)
INSTANCE_PORT = os.environ.get("INSTANCE_PORT", None)
TIDAL_LOGIN = os.environ.get("TIDAL_LOGIN", None)
PASSWORD = os.environ.get("TIDAL_PASSWORD", None)


class TelegramMessages:
    """Sending Messages via Telegram"""

    def __init__(self):

        if not TELEGRAM_API_KEY or not RECEIVER_ID:
            raise AssertionError(
                "Telegram APi key or receiver's chat id was not found in environment."
            )
        else:
            pass

        self.api_key = TELEGRAM_API_KEY
        self.receiver_id = RECEIVER_ID

        self.server_hostname = socket.gethostname()
        self.server_ip = requests.get("https://ipinfo.io/ip").content.decode("utf-8")

    def make_request(self, message):
        """Base sending message via API method"""
        try:
            requests.post(
                "https://api.telegram.org/bot{0}/sendMessage?chat_id={1}&parse_mode=Markdown&text={2}".format(
                    self.api_key, self.receiver_id, message
                )
            )
        except ConnectionError:
            pass

    def subscription_expire_message(self, container_id, container_port):
        message = (
            "The subscription has ended!\n"
            "Container with ID {0} was stopped.\n"
            "Server hostname: {1}\n"
            "Instance address: {2}:{3}".format(
                container_id, self.server_hostname, self.server_ip, container_port
            )
        )
        self.make_request(message)


class RemoteApiServer:
    """Sending and receiving Docker instances in remote server"""

    def __init__(self):
        self.api_address = REMOTE_API_SERVER_URL
        self.api_key = REMOTE_API_SERVER_KEY
        self.server_instance_ip = (
            urllib.request.urlopen("https://ipinfo.io/ip").read().decode("utf-8")
        )
        self.server_instance_port = INSTANCE_PORT

    def update_instance_status(
        self, instance_name: str, is_active: bool, log_message=""
    ):
        """Update instance status"""
        args = locals()
        del args["self"]
        params = str(urllib.parse.urlencode(args)).strip()
        request = requests.post(
            self.api_address + "/api/update_instance_status?" + params
        )

    def add_instance(
        self,
        instance_name: str,
        is_active: bool,
        log_message="",
        service_provider="PQ",
    ):
        """Adding new instance"""
        args = locals()
        del args["self"]
        args.update(
            {
                "email": TIDAL_LOGIN,
                "password": PASSWORD,
                "ip": self.server_instance_ip,
                "port": self.server_instance_port,
            }
        )
        params = urllib.parse.urlencode(args)
        request = requests.post(self.api_address + "/api/add_instance?" + str(params))
        response = json.loads(request.content)

        if response.get("status") != "200":
            self.update_instance_status(
                instance_name, True, "Started existing container."
            )
