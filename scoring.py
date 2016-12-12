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
    # The function returns a dictionary with a tuple of the Reputation score and the rank within the list
    pimranking = {}
    for key in pimrank_spread:
        pimranking[key] = (pimrank_spread[key], pimrank_ordered.index(key))
    return pimranking


def mock_get_ranking(database, pov_public_key):
    identities = database.get_identities()
    identities.remove(pov_public_key)
    identities.sort(key=lambda x: str(x))
    return identities


def calculate_ranking_similarity(ranking_subset, ranking):
    """ Calculate the ranking similarity between two lists of ranked peers,
    based on the definition in "Exploiting Graph Properties for Decentralized
    Reputation Networks" by Dimitra Gkorou, available at:
    http://repository.tudelft.nl/islandora/object/uuid:0fc40431-61ce-4bf6-b028-37c316e3e6b7
    (page 95)"""
    if not (ranking and ranking_subset):
        return 0
    r_w = sorted(ranking_subset, key=lambda x: ranking[x][1], reverse=True)

    # D is a normalisation factor
    D = 0
    for public_key in ranking_subset:
        score, rank = ranking[public_key][0], ranking[public_key][1]
        inverse_rank = r_w.index(public_key)

        D += score * (rank - inverse_rank) ** 2

    difference = 0
    for public_key in ranking_subset:
        score, rank = ranking[public_key][0], ranking[public_key][1]
        subset_rank = ranking_subset[public_key][1]
        difference += score * (rank - subset_rank) ** 2

    if D == 0:
        print "Ranking Similarity Edge case: normalisation factor is 0 "
        return 0.5
    return 1-difference/float(D)
