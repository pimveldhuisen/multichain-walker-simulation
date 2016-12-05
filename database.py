import base64
from sqlite3 import Connection

class DatabaseBlock:
    """ DataClass for a multichain block. """

    def __init__(self, data):
        """ Create a block from data """
        # Common part
        self.public_key_requester = str(data[0])
        self.public_key_responder = str(data[1])
        self.up = data[2]
        self.down = data[3]
        # Requester part
        self.total_up_requester = data[4]
        self.total_down_requester = data[5]
        self.sequence_number_requester = data[6]
        self.previous_hash_requester = str(data[7])
        self.signature_requester = str(data[8])
        self.hash_requester = str(data[9])
        # Responder part
        self.total_up_responder = data[10]
        self.total_down_responder = data[11]
        self.sequence_number_responder = data[12]
        self.previous_hash_responder = str(data[13])
        self.signature_responder = str(data[14])
        self.hash_responder = str(data[15])

        self.insert_time = data[16]

schema = u"""
CREATE TABLE IF NOT EXISTS multi_chain(
 public_key_requester		TEXT NOT NULL,
 public_key_responder		TEXT NOT NULL,
 up                         INTEGER NOT NULL,
 down                       INTEGER NOT NULL,

 total_up_requester         UNSIGNED BIG INT NOT NULL,
 total_down_requester       UNSIGNED BIG INT NOT NULL,
 sequence_number_requester  INTEGER NOT NULL,
 previous_hash_requester	TEXT NOT NULL,
 signature_requester		TEXT NOT NULL,
 hash_requester		        TEXT PRIMARY KEY,

 total_up_responder         UNSIGNED BIG INT NOT NULL,
 total_down_responder       UNSIGNED BIG INT NOT NULL,
 sequence_number_responder  INTEGER NOT NULL,
 previous_hash_responder	TEXT NOT NULL,
 signature_responder		TEXT NOT NULL,
 hash_responder		        TEXT NOT NULL,

 insert_time                TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
 );
"""


class Database:
    def __init__(self, dbpath, block_limit=None):
        self.dbpath = dbpath
        self.connection = Connection(dbpath)
        self.cursor = self.connection.cursor()
        self.cursor.executescript(schema)
        assert self.cursor is not None, "Database.close() has been called or Database.open() has not been called"
        assert self.connection is not None, "Database.close() has been called or Database.open() has not been called"
        self.time_limit = self._set_block_limit(block_limit)

    def _set_block_limit(self, block_limit):
        if block_limit:
            assert type(block_limit) is int
            assert block_limit > 0
            time_limit_query = u"SELECT MAX(insert_time) FROM " \
                               u"(SELECT insert_time FROM multi_chain ORDER BY insert_time LIMIT ?)"
            return self.cursor.execute(time_limit_query, [str(block_limit)]).fetchone()
        else:
            # If no time limit is to be set, we set the End of Unix Time as the limit
            time_limit_query = u"SELECT datetime(2147483647, 'unixepoch')"
            return self.cursor.execute(time_limit_query).fetchone()

    def get_identities(self):
        db_query = u"SELECT key " \
                   u"FROM (SELECT public_key_requester AS key FROM multi_chain WHERE insert_time <= ?" \
                   u"UNION SELECT public_key_responder AS key FROM multi_chain WHERE insert_time <= ?)"
        data = self.time_limit + self.time_limit
        db_result = self.cursor.execute(db_query, data).fetchall()
        return map(lambda x: x[0], db_result)

    def get_blocks(self, public_key):
        """
        Returns database blocks for the relevant public key
        :param public_key: The public key of the relevant peer
        :return A list of DB Blocks for the relevant public key
        """
        db_query = u"SELECT public_key_requester, public_key_responder, up, down, " \
                   u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, " \
                   u"signature_requester, hash_requester, " \
                   u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, " \
                   u"signature_responder, hash_responder, insert_time " \
                   u"FROM (" \
                   u"SELECT *, sequence_number_requester AS sequence_number," \
                   u" public_key_requester AS public_key FROM `multi_chain` " \
                   u"UNION " \
                   u"SELECT *, sequence_number_responder AS sequence_number," \
                   u" public_key_responder AS public_key FROM `multi_chain`) " \
                   u"WHERE public_key = ? AND " \
                   u"insert_time <= ?" \
                   u"ORDER BY sequence_number ASC "
        try:
            db_result = self.cursor.execute(db_query, (public_key,) + self.time_limit).fetchall()
        except Exception:
            print public_key
            raise
        return [DatabaseBlock(db_item) for db_item in db_result]

    def add_blocks(self, blocks):
        """
        Persist blocks
        :param blocks: The data that will be saved.
        """
        for block in blocks:
            data = (buffer(block.public_key_requester), buffer(block.public_key_responder), block.up, block.down,
                    block.total_up_requester, block.total_down_requester,
                    block.sequence_number_requester, buffer(block.previous_hash_requester),
                    buffer(block.signature_requester), buffer(block.hash_requester),
                    block.total_up_responder, block.total_down_responder,
                    block.sequence_number_responder, buffer(block.previous_hash_responder),
                    buffer(block.signature_responder), buffer(block.hash_responder))

            self.cursor.execute(
                u"INSERT OR IGNORE INTO multi_chain (public_key_requester, public_key_responder, up, down, "
                u"total_up_requester, total_down_requester, sequence_number_requester, previous_hash_requester, "
                u"signature_requester, hash_requester, "
                u"total_up_responder, total_down_responder, sequence_number_responder, previous_hash_responder, "
                u"signature_responder, hash_responder) "
                u"VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                data)
        self.cursor.connection.commit()

    def get_number_of_blocks_in_db(self):
        db_query = u"SELECT COUNT(*) FROM multi_chain WHERE insert_time <= ?;"
        db_result = self.cursor.execute(db_query, self.time_limit).fetchone()
        return db_result[0]



