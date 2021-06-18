import eel
from client.oqs_client import OQSClient
import sys

print(sys.path)

eel.init('web')


@eel.expose
def contact_connection_request(uuid):
    result = oqs_client.contact_connection_request(uuid)
    return result

@eel.expose
def get_uuid():
    uuid = oqs_client.get_uuid()
    return uuid

@eel.expose
def get_name():
    name = oqs_client.get_name()
    return name

@eel.expose
def load_chat_overview():
    chat_overview = oqs_client.load_chat_overview()
    return chat_overview

@eel.expose
def load_chat_history():
    chat_history = oqs_client.load_chat_history()
    return chat_history

@eel.expose
def send_message(uuid: str, message: str):
    oqs_client.send_msg(contact_uuid=uuid, msg=message)

oqs_client = OQSClient(name=sys.argv[1], eel=eel)
oqs_client.connect()

eel.start(
    'index.html',
    mode='chrome',
    size=(1200, 800),
    port=0
)
