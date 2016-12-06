import networkx as nx


class DatabaseAdaptor:
    """
    The Adaptor class serves as a way to create networkx DiGraph objects
    from a database file
    """
    def __init__(self, database):
        self.database = database

    def iterate_blocks(self, filter_date=None):
        if filter_date:
            raise NotImplementedError

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


        db_result = self.database.cursor.execute(db_query).fetchall()
        string_results = []
        for db_item in db_result:
            string_results.append(map(lambda x: str(x), db_item))
        return string_results

    def create_ordered_interaction_graph(self, filter_date=None):
        graph = nx.DiGraph()

        for interaction in self.iterate_blocks(filter_date):
            pubkey_requester = interaction[0]
            pubkey_responder = interaction[1]

            sequence_number_requester = int(interaction[6])
            sequence_number_responder = int(interaction[12])
            contribution_requester = int(interaction[2])
            contribution_responder = int(interaction[3])

            graph.add_edge((pubkey_requester, sequence_number_requester),
                           (pubkey_requester, sequence_number_requester + 1),
                           contribution=contribution_requester)
            graph.add_edge((pubkey_requester, sequence_number_requester),
                           (pubkey_responder, sequence_number_responder + 1),
                           contribution=contribution_responder)

            graph.add_edge((pubkey_responder, sequence_number_responder),
                           (pubkey_responder, sequence_number_responder + 1),
                           contribution=contribution_responder)
            graph.add_edge((pubkey_responder, sequence_number_responder),
                           (pubkey_requester, sequence_number_requester + 1),
                           contribution=contribution_requester)

        return graph
