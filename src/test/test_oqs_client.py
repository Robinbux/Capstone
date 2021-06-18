from unittest import TestCase
import sqlite3
import os
import uuid
import oqs
import eel
import base64
from threading import Thread
import json

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

class TestOQSClient(TestCase):
    pass
    # --------------------------------------------
    # PREPARATION FUNCTIONS AND VARIABLES
    # --------------------------------------------

    # def setUp(self):
    #     self.setUpDB()
    #
    # def setUpDB(self):
    #     self.connection = sqlite3.connect(DB_FILE_NAME, check_same_thread=False)
    #     self.connection.row_factory = sqlite3.Row
    #     self.cursor = self.connection.cursor()
    #     setup_file = open(CLIENT_DB_SETUP_PATH)
    #     setup_file_str = setup_file.read()
    #     self.cursor.executescript(setup_file_str)
    #     self.connection.commit()
    #
    # def setUpStandardVariables(self):
    #     pass
    #     # self.__pub_key = oqs_client.generate_keypair()
    #     # self.__private_key = oqs_client.export_secret_key()
    #     #
    #     # self.uuid_one = str(uuid.uuid4())
    #     # self.name_one = "John Doe"
    #     # self.public_key_one = oqs_client.generate_keypair()
    #     # self.private_key_one = oqs_client.export_secret_key()
    #     # self.seed_phrase, self.seed_hash = generate_random_seed_phrase()
    #
    # def tearDown(self):
    #     self.tearDownDB()
    #
    # def tearDownDB(self):
    #     # "Clear" DB by removing the file
    #     print("TEAR DOWN")
    #     os.remove(DB_FILE_NAME)
    #
    # def create_personal_account(
    #         self,
    #         uuid: str = str(UUID_ONE),
    #         name: str = NAME_ONE,
    #         private_key: bytes = PRIVATE_KEY_ONE,
    #         public_key: bytes = PUBLIC_KEY_ONE,
    #         seed_hash: bytes = SEED_HASH_ONE):
    #     self.cursor.execute("""
    #                 INSERT INTO personal_information
    #                 VALUES (
    #                     :uuid,
    #                     :name,
    #                     :privateKey,
    #                     :publicKey,
    #                     :seedHash
    #                 )
    #             """, {
    #         "uuid": uuid,
    #         "name": name,
    #         "privateKey": private_key,
    #         "publicKey": public_key,
    #         "seedHash": seed_hash
    #     })
    #     self.connection.commit()
    #
    # def add_contact(self, contact: Contact):
    #     self.cursor.execute("""
    #                     INSERT INTO contacts
    #                     VALUES (
    #                         :uuid,
    #                         :name,
    #                         :publicKey,
    #                         :sharedSecret,
    #                         :sharedCiphertext
    #                     )
    #                 """, {
    #         "uuid": contact.contact_uuid,
    #         "name": contact.contact_name,
    #         "publicKey": contact.contact_pub_key,
    #         "sharedSecret": contact.shared_secret,
    #         "sharedCiphertext": contact.shared_ciphertext
    #     })
    #     self.connection.commit()
    #
    # def start_server(self):
    #     self.server = OQSServer()
    #     self.server.start()
    #
    # def start_server_thread(self):
    #     self.server_thread = Thread(target=self.start_server)
    #     self.server_thread.start()
    #
    # def close_server(self):
    #     self.server.close()
    #
    # # --------------------------------------------
    # # _check_if_client_has_account
    # # --------------------------------------------
    # def test_check_if_client_has_account_true(self):
    #     global NAME_ONE
    #
    #     self.create_personal_account()
    #     oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
    #     self.assertTrue(oqs_client._check_if_client_has_account)
    #
    # def test_check_if_client_has_account_false(self):
    #     print("START TEST 2")
    #     global NAME_ONE
    #
    #     oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
    #     self.assertFalse(oqs_client._check_if_client_has_account())
    #
    # # --------------------------------------------
    # # _load_contacts
    # # --------------------------------------------
    # def test_load_contacts_equals(self):
    #     global CONTACT_ONE
    #     global CONTACT_TWO
    #
    #     oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
    #     self.add_contact(CONTACT_ONE)
    #     self.add_contact(CONTACT_TWO)
    #
    #     oqs_client._load_contacts()
    #
    #     self.assertEqual(oqs_client._contacts[0], CONTACT_ONE)
    #     self.assertEqual(oqs_client._contacts[1], CONTACT_TWO)
    #
    # def test_load_contacts_not_equals(self):
    #     global CONTACT_TWO
    #
    #     oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
    #     self.add_contact(CONTACT_ONE)
    #
    #     oqs_client._load_contacts()
    #
    #     self.assertNotEquals(oqs_client._contacts[0], CONTACT_TWO)

    # --------------------------------------------
    # _handle_incoming_message
    # --------------------------------------------
    # def test_handle_incoming_message_new_contact(self):
    #     request = {
    #         "senderUUID": str(CONTACT_UUID_ONE),
    #         "ciphertext": base64.b64encode(CONTACT_CIPHERTEXT_ONE).decode('ascii'),
    #         "senderName": CONTACT_NAME_ONE,
    #         "senderPublicKey": base64.b64encode(CONTACT_PUBLIC_KEY_ONE).decode('ascii'),
    #     }
    #
    #     oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
    #     oqs_client._handle_incoming_message(request)
    #
    #     # Check that contact is added nad generated key alligns
    #     self.assertEqual(oqs_client._contacts[0], CONTACT_ONE)


    # --------------------------------------------
    # connect
    # --------------------------------------------
    # def test_connect_no_server(self):
    #     print("START TEST 5")
    #     oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
    #     with self.assertRaises(ConnectionRefusedError):
    #         oqs_client.connect()
    #
    # def test_connect_new_account(self):
    #     print("START TEST 6")
    #     self.start_server_thread()
    #
    #     oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
    #     request_json = oqs_client.connect()
    #     print("**********************")
    #     print("**********************")
    #     print(request_json)
    #     print("**********************")
    #     print("**********************")
    #
    #     #self.close_server()
    #
    # #def test_connect_old_account(self):


