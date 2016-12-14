import random
import unittest

from database import Database
from scoring import get_ranking, calculate_ranking_similarity


class TestRankingSimilarity(unittest.TestCase):

    def test_ranking_identical(self):
        superset = {}
        superset['A'] = (200, 0)
        superset['B'] = (150, 1)
        superset['C'] = (100, 2)
        superset['D'] = (50, 3)
        superset['E'] = (20, 4)

        subset = {}
        subset['A'] = (200, 0)
        subset['B'] = (150, 1)
        subset['C'] = (100, 2)
        subset['D'] = (50, 3)
        subset['E'] = (20, 4)

        ranking_similarity = calculate_ranking_similarity(subset, superset)

        self.assertEqual(ranking_similarity, 1)

    def test_ranking_different(self):
        superset = {}
        superset['A'] = (200, 0)
        superset['B'] = (150, 1)
        superset['C'] = (100, 2)
        superset['D'] = (50, 3)
        superset['E'] = (20, 4)

        subset = {}
        subset['A'] = (250, 0)
        subset['D'] = (200, 1)
        subset['C'] = (100, 2)

        ranking_similarity = calculate_ranking_similarity(subset, superset)

        assert ranking_similarity < 1
        assert ranking_similarity > 0

    def test_ranking_edge_case(self):
        superset = {}
        superset['A'] = (200, 0)
        superset['B'] = (150, 1)
        superset['C'] = (0, 2)

        subset = {}
        subset['C'] = (0, 1)
        subset['B'] = (1, 0)

        ranking_similarity = calculate_ranking_similarity(subset, superset)

        assert ranking_similarity < 1
        assert ranking_similarity > 0

    def test_ranking_integrated(self):

        global_database = Database("../multichain.db", 100)
        personal_database = Database("temp.db", None)
        public_key = random.choice(global_database.get_identities())
        personal_database.add_blocks(global_database.get_blocks(public_key))
        global_ranking = get_ranking(global_database, public_key)
        personal_ranking = get_ranking(personal_database, public_key)

        ranking_similarity = calculate_ranking_similarity(personal_ranking, global_ranking)
        assert ranking_similarity <= 1
        assert ranking_similarity >= 0

    def test_ranking_integrated_full_database(self):

        global_database = Database("../multichain.db", 100)
        personal_database = Database("temp.db", None)
        public_key = random.choice(global_database.get_identities())
        for public_key in global_database.get_identities():
            personal_database.add_blocks(global_database.get_blocks(public_key))
        global_ranking = get_ranking(global_database, public_key)
        personal_ranking = get_ranking(personal_database, public_key)

        ranking_similarity = calculate_ranking_similarity(personal_ranking, global_ranking)

        self.assertEqual(ranking_similarity, 1)


