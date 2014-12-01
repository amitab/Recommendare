from pymongo import MongoClient

from Recommendare import Recommendare
from usersimilarity import UserSimilarity
from slopeone import SlopeOne

class systemTester:

    def run_test(self):
        client = MongoClient('localhost', 27017)
        self.db = client.hypertarget_ads

        failed = 0
        passed = 0

        if self.test_predict_rating() is False:
            failed += 1
        else:
            passed += 1

        if self.test_k_neighbours() is False:
            failed += 1
        else:
            passed += 1

        if self.test_recommend() is False:
            failed += 1
        else:
            passed += 1

        print "--------------------------------------------------------------------------------"
        print "PASSED: " + str(passed)
        print "FAILED: " + str(failed)

        return


    def test_predict_rating(self):

        slopeone = SlopeOne(self.db)
        result = slopeone.predict_rating(479, 2)
        if result is False:
            print "Test Case: PREDICT RATING: FAIL"
        else:
            print "Test Case: PREDICT RATING: PASS"

        return result

    def test_k_neighbours(self):

        usersimilarity = UserSimilarity(self.db)
        result = usersimilarity.find_k_nearest(479, 3)

        if result is False:
            print "Test Case: K NEIGHBOURS: FAIL"
        else:
            print "Test Case: K NEIGHBOURS: PASS"

        return result

    def test_recommend(self):

        recommender = Recommendare()
        result = recommender.recommend(479)

        if result is False:
            print "Test Case: RECOMMEND: FAIL"
        else:
            print "Test Case: RECOMMEND: PASS"

        return result


tester = systemTester()
tester.run_test()
