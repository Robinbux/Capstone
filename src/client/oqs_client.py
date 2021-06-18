import oqs
from threading import Thread
from socket import AF_INET, socket, SOCK_STREAM
import ssl
import logging
from util.oqs_utils import RequestType
from dataclasses import dataclass
import base64
import sqlite3
import json
import time

logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# Key encapsulation Algorithm
kemalg = "Kyber512"
client = oqs.KeyEncapsulation(kemalg)


@dataclass(eq=True, frozen=True)
class Contact:
    contact_name: str
    contact_uuid: str
    contact_pub_key: bytes
    shared_ciphertext: bytes
    shared_secret: bytes

DB_PATH = "client/pq-chat-client.db"
TEST_DB_PATH = "test/pq-chat-client.db"

class OQSClient():

    def __init__(self, eel, name: str, port: int = 33000, hostname='localhost', bufsize: int = 50000, test=False):
        self._eel = eel
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._name = name
        self._receive_thread = Thread(target=self._receive_msg)

        _context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        _context.verify_mode = ssl.CERT_REQUIRED
        _context.load_verify_locations('../pqca/ca/falcon512_CA.crt')

        _socket_temp = socket(AF_INET, SOCK_STREAM, 0)
        self._socket = _context.wrap_socket(_socket_temp, server_hostname=hostname, server_side=False)
        self._host = hostname
        self._port = port
        self._bufsize = bufsize
        self._address = (hostname, port)
        self._connecte_with_second_client = False
        self._contacts = []
        self._test = test

        # DB Preparation
        self._setup_db()
        self._load_contacts()
        self.__client_has_acccount = self._check_if_client_has_account()

    def _setup_db(self):
        self._logger.info("Setting up Database...")
        db_path = DB_PATH if not self._test else TEST_DB_PATH
        print(f"PATH: {db_path}")
        self._connection = sqlite3.connect(DB_PATH if not self._test else TEST_DB_PATH, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._cursor = self._connection.cursor()

        setup_file = open("client/setup-client.sql")
        setup_file_str = setup_file.read()
        self._cursor.executescript(setup_file_str)
        self._connection.commit()

    def _check_if_client_has_account(self) -> bool:
        rows = self._cursor.execute("SELECT * FROM personal_information").fetchall()
        return len(rows) >= 1

    def _load_contacts(self):
        contacts = self._cursor.execute("SELECT * FROM contacts").fetchall()
        for db_contact in contacts:
            contact = Contact(
                contact_name=db_contact['name'],
                contact_uuid=db_contact['uuid'],
                contact_pub_key=db_contact['public_key'],
                shared_ciphertext=db_contact['shared_ciphertext'],
                shared_secret=db_contact['shared_secret']
            )
            self._contacts.append(contact)

    def connect(self):
        try:
            self._socket.connect(self._address)
        except ConnectionRefusedError:
            self._logger.error(f"Unable to connect with server. Address: {self._address}")
            raise

        self._logger.info(f"Connected with host {self._host} on port {self._port}")

        # If client is new, the server needs to generate a UUID
        if not self.__client_has_acccount:
            self._logger.info(f"No Account found!")
            self.__pub_key = client.generate_keypair()
            self.__private_key = client.export_secret_key()
            payload = {}
            payload['requestType'] = RequestType.NEW_ACCOUNT_REQUEST
            payload['publicKey'] = base64.b64encode(self.__pub_key).decode('ascii')
            payload['name'] = self._name
            json_data = json.dumps(payload)
            self._socket.send(json_data.encode())
        else:
            # Logging in
            self._logger.info("Logging in")
            self._cursor.execute('select * from personal_information')
            personal_information = self._cursor.fetchone()
            self.__uuid = personal_information['uuid']
            payload = {}
            payload['requestType'] = RequestType.LOGIN_REQUEST
            payload['UUID'] = self.__uuid
            payload['seedHash'] = base64.b64encode(personal_information['seed_hash']).decode('ascii')
            json_data = json.dumps(payload)
            self._socket.send(json_data.encode())
        self._receive_thread.start()
        return json_data

    def _xor_msg_with_shared_secret(self, msg, secret):
        return bytes([_a ^ _b for _a, _b in zip(msg, secret)])

    def _handle_incoming_message(self, request_json):
        # Check if client is known or new
        print(f"REQUEST JSON : {request_json}")
        sender_uuid = request_json['senderUUID']
        sender = next((contact for contact in self._contacts if str(contact.contact_uuid) == sender_uuid), None)
        if sender is None:
            print("NEW CONTACT")
            print("Generating Shared secret...")
            print(f"REQUEST JSON: {request_json}")
            shared_secret = client.decap_secret(base64.b64decode(request_json['ciphertext']))
            sender = Contact(
                contact_name=request_json['senderName'],
                contact_uuid=sender_uuid,
                contact_pub_key=base64.b64decode(request_json['senderPublicKey']),
                shared_ciphertext=base64.b64decode(request_json['ciphertext']),
                shared_secret=shared_secret
            )
            self._contacts.append(sender)
            self._cursor.execute("""
            INSERT INTO contacts 
            VALUES (
                :uuid, 
                :name, 
                :publicKey, 
                :sharedSecret,
                :sharedCiphertext
            ) 
            """, {
                "uuid": sender_uuid,
                "name": request_json['senderName'],
                "publicKey": base64.b64decode(request_json['senderPublicKey']),
                "sharedSecret": shared_secret,
                "sharedCiphertext": base64.b64decode(request_json['ciphertext'])
            })
            self._connection.commit()

        base64_decoded_msg = base64.b64decode(request_json['message'])
        decrypted_msg = self._xor_msg_with_shared_secret(base64_decoded_msg, secret=sender.shared_secret)
        msg = decrypted_msg.decode()

        payload = {}
        payload['message'] = msg
        payload['senderName'] = sender.contact_name
        payload['senderUUID'] = sender.contact_uuid

        self._cursor.execute("""
            INSERT INTO chat_history 
            VALUES (
                :message, 
                :contact, 
                :sentBy,
                :date
            ) 
        """, {
            "message": msg,
            "contact": sender.contact_uuid,
            "sentBy": "CONTACT",
            "date": int(time.time())
        })
        self._connection.commit()

        self._eel.handleIncomingMessage(json.dumps(payload))

    def _handle_connect_with_contact_response(self, request_json):
        if request_json['contactExists']:
            contact_pub_key: bytes = base64.b64decode(request_json['contactPublicKey'])
            ciphertext, shared_secret = client.encap_secret(contact_pub_key)
            contact = Contact(
                contact_name=request_json['contactName'],
                contact_uuid=request_json['contactUUID'],
                contact_pub_key=request_json['contactPublicKey'],
                shared_ciphertext=ciphertext,
                shared_secret=shared_secret
            )
            self._contacts.append(contact)

            self._cursor.execute("""
                INSERT INTO contacts 
                VALUES (
                    :uuid, 
                    :name, 
                    :publicKey, 
                    :sharedSecret,
                    :sharedCiphertext
                ) 
            """, {
                "uuid": request_json['contactUUID'],
                "name": request_json['contactName'],
                "publicKey": request_json['contactPublicKey'],
                "sharedSecret": shared_secret,
                "sharedCiphertext": ciphertext
            })
            self._connection.commit()
        self._eel.handleAddContactResponse(json.dumps(request_json))

    def _save_personal_information(self, request_json):
        self._logger.info(f"Saving personal data with UUID: {request_json['UUID']}")
        self._cursor.execute("""
            INSERT INTO personal_information 
            VALUES (
                :uuid, 
                :name, 
                :privateKey, 
                :publicKey,
                :seedHash
            ) 
        """, {
            "uuid": request_json['UUID'],
            "name": self._name,
            "privateKey": self.__private_key,
            "publicKey": self.__pub_key,
            "seedHash": base64.b64decode(request_json['seedHash'])
        }
                             )
        self._connection.commit()
        self.__uuid = request_json['UUID']

    def _receive_msg(self):
        while True:
            msg = self._socket.recv(self._bufsize)

            request_json = json.loads(msg.decode())
            request_type_str = request_json["requestType"]
            request_type = RequestType[request_type_str]
            print(type(request_type))

            if request_type == RequestType.SEND_MESSAGE_REQUEST:
                self._handle_incoming_message(request_json)

            elif request_type == RequestType.ASSIGN_UUID_AND_SEED:
                print("*************************")
                print("ASSIGN UUID AND SEED")
                self._save_personal_information(request_json)

            elif request_type == RequestType.CONNECT_WITH_CONTACT_RESPONSE:
                print("*************************")
                print("RECEIVED CONNECT WITH CONTACT")
                self._handle_connect_with_contact_response(request_json)

    def contact_connection_request(self, contact_uuid: str) -> int:
        payload = {}
        payload['requestType'] = RequestType.CONNECT_WITH_CONTACT_REQUEST
        payload['contactUUID'] = contact_uuid
        json_data = json.dumps(payload)
        return self._socket.send(json_data.encode())




    def send_msg(self, contact_uuid: str, msg: str):
        # Get contact by UUID
        contact = next((contact for contact in self._contacts if str(contact.contact_uuid) == contact_uuid), None)

        self._cursor.execute("""
            INSERT INTO chat_history 
            VALUES (
                :message, 
                :contact,
                :sentBy,
                :date
            ) 
        """, {
            "message": msg,
            "contact": contact_uuid,
            "sentBy": "ME",
            "date": int(time.time())
        })
        self._connection.commit()

        # Encode message
        encoded_message = self._xor_msg_with_shared_secret(msg=msg.encode(), secret=contact.shared_secret)

        payload = {}
        payload['requestType'] = RequestType.SEND_MESSAGE_REQUEST
        payload['contactUUID'] = contact_uuid
        payload['message'] = base64.b64encode(encoded_message).decode('ascii')


        payload['ciphertext'] = base64.b64encode(contact.shared_ciphertext).decode('ascii')
        json_data = json.dumps(payload)

        self._socket.send(json_data.encode())

    # Frontend exposed methods:
    def get_uuid(self):
        return self.__uuid

    def get_name(self):
        return self._name

    def load_chat_overview(self):
        overview_list = []
        rows = self._cursor.execute("SELECT c.uuid, c.name FROM contacts c").fetchall()
        for row in rows:
            overview_list.append(dict(row))
        return json.dumps(overview_list)

    def load_chat_history(self):
        history_list = []
        rows = self._cursor.execute("SELECT * FROM chat_history").fetchall()
        for row in rows:
            history_list.append(dict(row))
        return json.dumps(history_list)

