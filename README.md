# Quantum Safe Communication

Modern encryption algorithms are often based on methods like prime factorization and 
will therefore become obsolete in the post quantum era, where algorithms like Shor’s 
algorithm are able to do these tasks in a reasonable amount of time. 
For that time, people are working on quantum safe encryption, 
which is set to be secure for quantum computers as well. 
In this Capstone Project, I have written a quantum-safe chat application, 
using said algorithms for a quantum- safe TLS communication between client and server and 
lastly a quantum-safe KEM(Key encapsulation mechanism) algorithm between client and client.

For a presentation video, please look [here]()


## Setup
For a manual reproduction, please install [liboqs-python](https://github.com/open-quantum-safe/liboqs-python) and the forked [openssl](https://github.com/open-quantum-safe/openssl). 

Install a custom Python version (Needed for the openssl verification)
```shell
export PYTHON_VERSION=3.9.5
wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz
tar -xvf Python-${PYTHON_VERSION}.tar.xz
rm Python-${PYTHON_VERSION}.tar.xz
```

Build liboqs
```shell
# Replace OPENSSL_PATH and LIBOQS_PATH with your installation path
cd ${LIBOQS_PATH}
mkdir build && cd build && cmake -GNinja -DCMAKE_INSTALL_PREFIX=${OPENSSL_PATH}/oqs .. \
    && ninja && ninja install
```

Build liboqs-openssl
```shell
cd ${OPENSSL_PATH}
./Configure no-shared linux-x86_64 -lm
./Configure --prefix=/Users/robinbux/quantum-new/openssl --openssldir=/Users/robinbux/quantum-new/openssl/ssl
make -j -l
```

Build Python
```shell
./configure --with-openssl=${OPENSSL_PATH} --with-http_ssl_module
```

### Create Certificates
Create private and public CA certs
```shell
export SIG_ALG="dilithium5"
mkdir ca && cd ca && ${OPENSSL_PATH}/apps/openssl req -x509 -new -newkey ${SIG_ALG} -keyout ${SIG_ALG}_CA.key \
    -out ${SIG_ALG}_CA.crt -nodes -subj "/CN=pq-cert CA" -days 365 \
    -config opt/openssl/apps/openssl.cnf
```
Create server private key
```shell
mkdir server && cd server && ${OPENSSL_PATH}/apps/openssl genpkey -algorithm ${SIG_ALG} -out ${SIG_ALG}_srv.key
```
Create certificate signing request
```shell
cd server && ${OPENSSL_PATH}/apps/openssl req -new -newkey ${SIG_ALG} -keyout ${SIG_ALG}_srv.key \
    -out ${SIG_ALG}_srv.csr -nodes -subj "/CN=pq-cert" \
    -config ${OPENSSL_PATH}/apps/openssl.cnf
```
Create ext file
```shell
echo $'authorityKeyIdentifier=keyid,issuer \n\
basicConstraints=CA:FALSE \n\
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment \n\
subjectAltName = @alt_names \n\
[alt_names] \n\
DNS.1 = localhost \n\
IP.1 = 127.0.0.1 ' > server/v3.ext
```
Let the CA sign the request
```shell
${OPENSSL_PATH}/apps/openssl x509 -req -in server/${SIG_ALG}_srv.csr -out server/${SIG_ALG}_srv.crt \
    -CA ca/${SIG_ALG}_CA.crt -CAkey ca/${SIG_ALG}_CA.key -CAcreateserial -days 365 -extfile v3.ext
```

## RUN
To run the application, you need to use the custom Python installation. Having that aliased as `pq-python`, you can start the server with
```shell
pq-python start_server.py
```
and the client with 
```shell
pq-python start_client.py ${NAME}
```
