CREATE TABLE IF NOT EXISTS clients
(
    uuid TEXT NOT NULL
        constraint contacts_pk
            primary key,
    name TEXT NOT NULL,
    public_key BLOB NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS clients_uuid_uindex
            ON clients (uuid);
