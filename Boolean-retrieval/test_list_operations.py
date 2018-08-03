import unittest
from list_operations import or_operation, and_operation, not_operation, and_not_operation

"""
    File name: test_list_operations.py
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 06/03/2018
    Python Version: 2.7
"""

class OrOperationTestCase(unittest.TestCase):
    def test_two_postings(self):
        l1 = [(1, 2), (2, 0), (3, 0)]
        l2 = [(3, 2), (5, 0), (6, 0)]
        l3 = []
        self.assertEqual([1, 2, 3, 5, 6], or_operation(l1, l2))
        self.assertEqual([1, 2, 3], or_operation(l1, l3))
        self.assertEqual([1, 2, 3], or_operation(l3, l1))

    def test_two_doc_id_lists(self):
        l1 = [1, 2, 3]
        l2 = [3, 5, 6]
        l3 = []
        self.assertEqual([1, 2, 3, 5, 6], or_operation(l1, l2))
        self.assertEqual([1, 2, 3], or_operation(l1, l3))
        self.assertEqual([1, 2, 3], or_operation(l3, l1))

    def test_one_posting_one_doc_id_list(self):
        l1 = [(1, 2), (2, 0), (3, 0)]
        l2 = [3, 5, 6]
        self.assertEqual([1, 2, 3, 5, 6], or_operation(l1, l2))
        l1 = [1, 2, 3]
        l2 = [(3, 2), (5, 0), (6, 0)]
        self.assertEqual([1, 2, 3, 5, 6], or_operation(l1, l2))


class NotOperationTestCase(unittest.TestCase):
    def test_posting(self):
        l1 = [(1, 2), (2, 0), (3, 0)]
        l_all = [1, 2, 3, 4, 5, 6, 10, 100, 999]
        self.assertEqual([4, 5, 6, 10, 100, 999], not_operation(l1, l_all))

    def test_doc_id_list(self):
        l1 = [1, 4, 10, 999]
        l_all = [1, 2, 3, 4, 5, 6, 10, 100, 999]
        self.assertEqual([2, 3, 5, 6, 100], not_operation(l1, l_all))

    def test_empty_list(self):
        l1 = [(1, 2), (2, 0), (3, 0)]
        l_all = []
        self.assertEqual([], not_operation(l1, l_all))
        l1 = [1, 4, 10, 999]
        self.assertEqual([], not_operation(l1, l_all))
        l1 = []
        l_all = [1, 2, 3, 4, 5, 6, 10, 100, 999]
        self.assertEqual(l_all, not_operation(l1, l_all))


class AndOperationTestCase(unittest.TestCase):
    def test_two_postings(self):
        l1 = [(1, 2), (2, 0), (3, 4), (99, 0), (100, 0)]
        l2 = [(3, 2), (5, 0), (6, 4), (100, 0), (120, 0)]
        self.assertEqual([3, 100], and_operation(l1, l2))
        l1 = [(7, 2), (99, 0), (100, 0)]
        l2 = [(7, 2), (99, 0), (100, 0)]
        self.assertEqual([7, 99, 100], and_operation(l1, l2))
        l1 = []
        l2 = [(7, 2), (99, 0), (100, 0)]
        self.assertEqual([], and_operation(l1, l2))
        self.assertEqual([], and_operation(l2, l1))

    def test_two_doc_id_lists(self):
        l1 = [9, 10, 11]
        l2 = [3, 5, 6]
        self.assertEqual([], and_operation(l1, l2))
        l1 = [7, 99, 100]
        l2 = [7, 99, 100]
        self.assertEqual([7, 99, 100], and_operation(l1, l2))
        l1 = []
        l2 = [7, 99, 100]
        self.assertEqual([], and_operation(l1, l2))
        self.assertEqual([], and_operation(l2, l1))

    def test_one_posting_one_doc_id_list(self):
        l1 = [(1, 2), (2, 0), (3, 0), (6,0)]
        l2 = [3, 5, 6]
        self.assertEqual([3, 6], and_operation(l1, l2))
        self.assertEqual([3, 6], and_operation(l2, l1))
        l1 = [1, 2, 3, 6]
        l2 = [(3, 2), (5, 0), (6, 0)]
        self.assertEqual([3, 6], and_operation(l1, l2))
        self.assertEqual([3, 6], and_operation(l2, l1))
        l1 = [1, 2, 3, 6, 16, 49, 69, 77, 90, 101, 150]
        l2 = [(3, 3), (49, 0), (86, 0), (87, 6), (88, 0), (89, 0), (90, 9), (91, 0), (101, 0), (133, 0), (144, 0), (170, 0)]
        self.assertEqual([3, 49, 90, 101], and_operation(l1, l2))
        self.assertEqual([3, 49, 90, 101], and_operation(l2, l1))

    def test_fully_utilize_skip_pointers(self):
        l1 = [(10, 2), (20, 0), (30, 4), (40, 0), (50, 6), (60, 0), (70, 0)]
        l2 = [70, 100, 101]
        self.assertEqual([70], and_operation(l1, l2))
        self.assertEqual([70], and_operation(l2, l1))
        l1 = [(10, 2), (20, 0), (30, 4), (40, 0), (50, 6), (60, 0), (70, 0)]
        l2 = [(1, 2), (2, 0), (3, 4), (50, 0), (70, 0), (82, 0)]
        self.assertEqual([50, 70], and_operation(l1, l2))
        self.assertEqual([50, 70], and_operation(l2, l1))

    def test_dont_utilize_skip_pointers(self):
        l1 = [(10, 2), (20, 0), (30, 4), (40, 0), (50, 6), (60, 0), (70, 0)]
        l2 = [11, 21, 31, 41, 50, 61, 71]
        self.assertEqual([50], and_operation(l1, l2))
        self.assertEqual([50], and_operation(l2, l1))


class AndNotOperationTestCase(unittest.TestCase):
    def test_two_postings(self):
        l1 = [(1, 2), (2, 0), (3, 4), (99, 0), (100, 0)]
        l2 = [(3, 2), (5, 0), (6, 4), (100, 0), (120, 0)]
        l_all = [1, 2, 3, 5, 6, 99, 100, 120]
        self.assertEqual([1, 2, 99], and_not_operation(l1, l2, l_all))
        l_all = [7, 99, 100]
        l1 = [(7, 2), (99, 0), (100, 0)]
        l2 = [(7, 2), (99, 0), (100, 0)]
        self.assertEqual([], and_not_operation(l1, l2, l_all))
        l_all = [7, 99, 100]
        l1 = []
        l2 = [(7, 2), (99, 0), (100, 0)]
        self.assertEqual([], and_not_operation(l1, l2, l_all))
        self.assertEqual([7, 99, 100], and_not_operation(l2, l1, l_all))

    def test_two_doc_id_lists(self):
        l_all = [3, 5, 6, 9, 10, 11]
        l1 = [9, 10, 11]
        l2 = [3, 5, 6]
        self.assertEqual([9, 10, 11], and_not_operation(l1, l2, l_all))
        self.assertEqual([9, 10, 11], and_not_operation(l1, l2, l_all))
        l_all = [7, 99, 100]
        l1 = [7, 99, 100]
        l2 = [7, 99, 100]
        self.assertEqual([], and_not_operation(l1, l2, l_all))
        l_all = [7, 99, 100]
        l1 = []
        l2 = [7, 99, 100]
        self.assertEqual([], and_not_operation(l1, l2, l_all))
        self.assertEqual([7, 99, 100], and_not_operation(l2, l1, l_all))

    def test_one_posting_one_doc_id_list(self):
        l_all = [1, 2, 3, 5, 6]
        l1 = [(1, 2), (2, 0), (3, 0), (6, 0)]
        l2 = [3, 5, 6]
        self.assertEqual([1, 2], and_not_operation(l1, l2, l_all))
        self.assertEqual([5], and_not_operation(l2, l1, l_all))
        l_all = [1, 2, 3, 5, 6]
        l1 = [1, 2, 3, 6]
        l2 = [(3, 2), (5, 0), (6, 0)]
        self.assertEqual([1, 2], and_not_operation(l1, l2, l_all))
        self.assertEqual([5], and_not_operation(l2, l1, l_all))
        l_all = [1, 2, 3, 6, 16, 49, 69, 77, 86, 87, 88, 89, 90, 91, 101, 133, 144, 150, 170]
        l1 = [1, 2, 3, 6, 16, 49, 69, 77, 90, 101, 150]
        l2 = [(3, 3), (49, 0), (86, 0), (87, 6), (88, 0), (89, 0), (90, 9), (91, 0), (101, 0), (133, 0), (144, 0), (170, 0)]
        self.assertEqual([1, 2, 6, 16, 69, 77, 150], and_not_operation(l1, l2, l_all))
        self.assertEqual([86, 87, 88, 89, 91, 133, 144, 170], and_not_operation(l2, l1, l_all))

    def test_empty_list(self):
        l_all = [1, 2, 3, 4, 5]
        l1 = []
        l2 = []
        self.assertEqual([], and_not_operation(l1, l2, l_all))
        l_all = [1, 2, 3, 4, 5]
        l1 = [1, 2, 3]
        l2 = []
        self.assertEqual([1, 2, 3], and_not_operation(l1, l2, l_all))
        self.assertEqual([], and_not_operation(l2, l1, l_all))
        l_all = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        l1 = [1, 2, 3]
        l2 = [1, 2, 3, 4, 5, 6]
        self.assertEqual([], and_not_operation(l1, l2, l_all))

        l1 = [1, 2, 3]
        l2 = [(1, 2), (2,0), (3,4), (4,0), (5,0), (6,0)]
        self.assertEqual([], and_not_operation(l1, l2, l_all))

        l1 = [(1,0), (2,0), (3,0)]
        l2 = [(1, 2), (2,0), (3,4), (4,0), (5,0), (6,0)]
        self.assertEqual([], and_not_operation(l1, l2, l_all))

        l1 = [(1, 2), (2,0), (3,4), (4,0), (5,0), (6,0)]
        l2 = [2, 4, 6]

        self.assertEqual([1, 3, 5], and_not_operation(l1, l2, l_all))

        l1 = [(1, 5), (10, 0), (100, 0), (1000, 0), (1008, 0), (10000, 10), (10002, 0), (10005, 0), (10011, 0), (10014, 0), (10015, 15), (10018, 0), (10025, 0), (10038, 0), (10041, 0), (10042, 20), (10043, 0), (10046, 0), (10048, 0), (10049, 0), (10052, 25), (10054, 0), (10057, 0), (10058, 0), (10062, 0), (10066, 30), (10067, 0), (10068, 0), (10071, 0), (10073, 0), (10078, 0)]
        l2 = [1, 10054, 10071, 10073]
        # print and_not_operation(l2, l1, l_all)
        # print and_not_operation(l1, l2, l_all)


if __name__ == '__main__':
    unittest.main()
