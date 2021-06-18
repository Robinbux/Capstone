CREATE TABLE IF NOT EXISTS personal_information
(
    uuid TEXT NOT NULL,
    name TEXT NOT NULL,
    private_key BLOB NOT NULL,
    public_key BLOB NOT NULL,
    seed_hash BLOB NOT NULL
);

CREATE TABLE IF NOT EXISTS contacts
(
    uuid TEXT NOT NULL
        constraint contacts_pk
            primary key,
    name TEXT NOT NULL,
    public_key BLOB NOT NULL,
    shared_secret BLOB NOT NULL,
    shared_ciphertext BLOB NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS contacts_uuid_uindex
            ON contacts (uuid);

CREATE TABLE IF NOT EXISTS chat_history
(
    message TEXT NOT NULL,
    contact TEXT NOT NULL,
    sentBy TEXT NOT NULL, -- "ME" or "CONTACT"
    date INTEGER NOT NULL, -- Represented as unix timestamp
    FOREIGN KEY(contact) REFERENCES contacts(uuid)
);
