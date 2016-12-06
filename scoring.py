import pimrank


def get_ranking(database, pov_public_key):
    """Get an list of peers (identified by public key) ordered by their score,
    such that the 'best' peer is the first item in the list and the 'worst' peer is the last item on the list.
    Scores are calculated from the point of view of the peer whose public key is supplied in the second argument,
    and is based on the database given in the first argument.
    The database must contain at least one block involving the point of view public key"""

    adaptor = pimrank.database_adaptor.DatabaseAdaptor(database)
    ordered_graph = adaptor.create_ordered_interaction_graph()

    personal_blocks = [block for block in ordered_graph.nodes() if block[0] == str(pov_public_key)]
    number_of_blocks = len(personal_blocks)
    try:
        personalisation = dict(zip(personal_blocks, [1.0 / number_of_blocks] * number_of_blocks))
    except:
        print pov_public_key
        print database.get_number_of_blocks_in_db()
        print [block[0] for block in ordered_graph.nodes()[1:20]]
        raise

    pimrank_spread = pimrank.pimrank.PimRank(ordered_graph, personalisation).compute()

    pimrank_ordered = sorted(pimrank_spread, key=pimrank_spread.__getitem__, reverse=True)
    return pimrank_ordered


def mock_get_ranking(database, pov_public_key):
    identities = database.get_identities()
    identities.remove(pov_public_key)
    identities.sort(key=lambda x: str(x))
    return identities


def calculate_rank_difference(ranking_a, ranking_b):
    """"""
    avg_rank_difference = 0
    for public_key in ranking_a + ranking_b:
        try:
            rank_a = float(ranking_a.index(public_key))/len(ranking_a)
        except ValueError:
            rank_a = 0.5
        try:
            rank_b = float(ranking_b.index(public_key))/len(ranking_b)
        except ValueError:
            rank_b = 0.5
        rank_difference = rank_a - rank_b
        avg_rank_difference += rank_difference/len(ranking_a + ranking_b)
    return avg_rank_difference
