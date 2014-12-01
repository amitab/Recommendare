from usersimilarity import UserSimilarity
from slopeone import SlopeOne

import unittest

class unitTester(unittest.TestCase):

    def setUp(self):
        pass

    def test_cosine_similarity(self):
        vector_x = [4.75, 4.5, 5, 4.25, 4]
        vector_y = [4, 3, 5, 2, 1]

        user_sim = UserSimilarity()

        self.assertAlmostEqual(0.935, user_sim.cosine_similarity(vector_x, vector_y), places = 3)

    def test_change_range(self):
        old_range_min = 0
        old_range_max = 100
        new_range_min = 0
        new_range_max = 1

        old_value = 80

        user_sim = UserSimilarity()

        self.assertAlmostEqual(0.8, user_sim.change_range(old_value, old_range_max, old_range_min, new_range_max, new_range_min), places = 1)

    def test_deviation(self):

        taylor_swift = {
            'Amy': 4,
            'Ben': 5,
            'Daisy': 5
        }

        PSY = {
            'Amy': 3,
            'Ben': 2,
            'Clara': 3.5
        }

        slope = SlopeOne()

        self.assertEqual(2, slope.deviation(taylor_swift, PSY)['deviation'])

if __name__ == '__main__':
    unittest.main()

