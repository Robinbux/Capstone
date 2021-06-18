from unittest import TestCase
import uuid
import oqs
import eel
from threading import Thread
import os
import sqlite3
import time

from util.security_util import generate_random_seed_phrase
from client.oqs_client import OQSClient, Contact
from server.oqs_server import OQSServer

DB_FILE_NAME = "test/pq-chat-client.db"
CLIENT_DB_SETUP_PATH = "client/setup-client.sql"

KEMALG = "Kyber512"

# --------------------------------------------
# Personal
# --------------------------------------------
CLIENT = oqs.KeyEncapsulation(KEMALG)
UUID_ONE = uuid.uuid4()
NAME_ONE = "John Doe"
PUBLIC_KEY_ONE = CLIENT.generate_keypair()
PRIVATE_KEY_ONE = CLIENT.export_secret_key()
SEED_PHRASE_ONE, SEED_HASH_ONE = generate_random_seed_phrase()

# --------------------------------------------
# Contact
# --------------------------------------------
CONTACT_CLIENT_ONE = oqs.KeyEncapsulation(KEMALG)
CONTACT_UUID_ONE = uuid.uuid4()
CONTACT_NAME_ONE = "Alan Turing"
CONTACT_PUBLIC_KEY_ONE = CONTACT_CLIENT_ONE.generate_keypair()
CONTACT_PRIVATE_KEY_ONE = CONTACT_CLIENT_ONE.export_secret_key()
CONTACT_SEED_PHRASE_ONE, CONTACT_SEED_HASH_ONE = generate_random_seed_phrase()
CONTACT_CIPHERTEXT_ONE, CONTACT_SHARED_SECRET_ONE = CLIENT.encap_secret(CONTACT_PUBLIC_KEY_ONE)

CONTACT_ONE = Contact(
    contact_name=CONTACT_NAME_ONE,
    contact_uuid=str(CONTACT_UUID_ONE),
    contact_pub_key=CONTACT_PUBLIC_KEY_ONE,
    shared_ciphertext=CONTACT_CIPHERTEXT_ONE,
    shared_secret=CONTACT_SHARED_SECRET_ONE
)

CONTACT_CLIENT_TWO = oqs.KeyEncapsulation(KEMALG)
CONTACT_UUID_TWO = uuid.uuid4()
CONTACT_NAME_TWO = "Ada Lovelace"
CONTACT_PUBLIC_KEY_TWO = CONTACT_CLIENT_TWO.generate_keypair()
CONTACT_PRIVATE_KEY_TWO = CONTACT_CLIENT_TWO.export_secret_key()
CONTACT_SEED_PHRASE_TWO, CONTACT_SEED_HASH_TWO = generate_random_seed_phrase()
CONTACT_CIPHERTEXT_TWO, CONTACT_SHARED_SECRET_TWO = CLIENT.encap_secret(CONTACT_PUBLIC_KEY_TWO)

CONTACT_TWO = Contact(
    contact_name=CONTACT_NAME_TWO,
    contact_uuid=str(CONTACT_UUID_TWO),
    contact_pub_key=CONTACT_PUBLIC_KEY_TWO,
    shared_ciphertext=CONTACT_CIPHERTEXT_TWO,
    shared_secret=CONTACT_SHARED_SECRET_TWO
)

server = OQSServer()
server_thread = None
def start_server():
    server.start()


def start_server_thread():
    server_thread = Thread(target=start_server)
    server_thread.start()

def stop_server_thread():
    print("STOP")
    server.stop_server()

class TestIntegration(TestCase):

    @classmethod
    def setUpClass(cls):
        print("Set up class")
        start_server_thread()

    @classmethod
    def tearDownClass(cls):
        print("TEAR DOWN CLASS")

    def tearDown(self):
        self.tearDownDB()

    def tearDownDB(self):
        # "Clear" DB by removing the file
        print("TEAR DOWN")
        os.remove(DB_FILE_NAME)

    # Tests
    def test_login(self):
        oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
        oqs_client.connect()
        time.sleep(1)
        print("AFTER SLEEP")
        self.assertFalse(oqs_client._client_has_acccount)
        # Now log in
        oqs_client_new = OQSClient(name=NAME_ONE, eel=eel, test=True)
        oqs_client_new.connect()
        time.sleep(1)
        self.assertTrue(oqs_client_new._client_has_acccount)

    def test_connect_with_contact(self):
        oqs_client_one = OQSClient(name=NAME_ONE, eel=eel, test=True)
        oqs_client_one.connect()
        time.sleep(1)
        oqs_client_two = OQSClient(name=NAME_ONE, eel=eel, test=True)
        oqs_client_two.connect()
        time.sleep(1)
        client_two_uuid = oqs_client_two.get_uuid()

        oqs_client_one.contact_connection_request(contact_uuid = client_two_uuid)
        time.sleep(1)
        self.assertEqual(oqs_client_one._contacts[0].contact_uuid, client_two_uuid)


    def test_send_message_between_clients(self):
        oqs_client_one = OQSClient(name=CONTACT_NAME_ONE, eel=eel, test=True)
        oqs_client_one.connect()
        time.sleep(5)

        oqs_client_two = OQSClient(name=CONTACT_NAME_TWO, eel=eel, test=True, other_db_path = "test/pq-chat-client-two.db")
        oqs_client_two.connect()
        time.sleep(5)

        client_two_uuid = oqs_client_two.get_uuid()

        oqs_client_one.contact_connection_request(contact_uuid=client_two_uuid)
        time.sleep(5)

        test_message_one = "New message from client one!"

        # Send from client one
        oqs_client_one.send_msg(contact_uuid=client_two_uuid, msg=test_message_one)
        time.sleep(5)

        # Verify that client two received
        chat_history_two = oqs_client_two.load_chat_history_list()

        self.assertEqual(len(chat_history_two), 1)
        self.assertEqual(chat_history_two[0]['message'], test_message_one)

        # Send message back
        test_message_two = "Reply from client two!"
        client_one_uuid = oqs_client_one.get_uuid()
        time.sleep(5)
        oqs_client_two.send_msg(contact_uuid=client_one_uuid, msg=test_message_two)
        time.sleep(5)

        # Verify that client one received
        chat_history_one = oqs_client_one.load_chat_history_list()
        self.assertEqual(len(chat_history_one), 1)
        self.assertEqual(chat_history_one[0]['message'], test_message_two)






