
def get_ranking(database, pov_public_key):
    """Get an list of peers (identified by public key) ordered by their score,
    such that the 'best' peer is the first item in the list and the 'worst' peer is the last item on the list.
    Scores are calculated from the point of view of the peer whose public key is supplied in the second argument,
    and is based on the database given in the first argument.
    The database must contain at least one block involving the point of view public key"""
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
