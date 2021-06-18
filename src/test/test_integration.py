from unittest import TestCase
import uuid
import oqs
import eel
from threading import Thread

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

class TestIntegration(TestCase):

    def start_server(self):
        self.server = OQSServer()
        self.server.start()

    def start_server_thread(self):
        self.server_thread = Thread(target=self.start_server)
        self.server_thread.start()

    def close_server(self):
        self.server.close()

    # Tests
    def test_login(self):
        self.start_server_thread()
        oqs_client = OQSClient(name=NAME_ONE, eel=eel, test=True)
        oqs_client.connect()
        self.assertTrue(True)



