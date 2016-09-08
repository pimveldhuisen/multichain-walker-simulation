from sqlite3 import Connection

from Tribler.community.multichain.database import DatabaseBlock


class Database:
    def __init__(self, dbpath):
        self.dbpath = dbpath
        self.connection = Connection(dbpath)
        self.cursor = self.connection.cursor()
        assert self.cursor is not None, "Database.close() has been called or Database.open() has not been called"
        assert self.connection is not None, "Database.close() has been called or Database.open() has not been called"

    def get_identities(self):
        db_query = u"SELECT key " \
                   u"FROM (SELECT public_key_requester AS key FROM multi_chain " \
                   u"UNION SELECT public_key_responder AS key FROM multi_chain)"
        db_result = self.cursor.execute(db_query).fetchall()
        return db_result

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
                   u"WHERE public_key = ? " \
                   u"ORDER BY sequence_number ASC "
        db_result = self.cursor.execute(db_query, public_key).fetchall()
        return [DatabaseBlock(db_item) for db_item in db_result]

