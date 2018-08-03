import unittest
import json
from nltk.tokenize import sent_tokenize, word_tokenize

from preprocess import preprocess
from reverse_polish_notation import get_postings, compute_rpn
from list_operations import or_operation, and_operation, not_operation, and_not_operation

"""
    File name: test_search.py
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 08/03/2018
    Python Version: 2.7
"""

def load_dict_file(dict_file):
    with open(dict_file, 'r') as dictionary_f:
        return json.load(dictionary_f)


dictionary_file = 'dictionary.test.txt'
postings_file = 'postings.test.txt'
term_dict = load_dict_file(dictionary_file)


def main(query):
    expr = preprocess(query, term_dict)
    if len(expr):
        doc_ids = compute_rpn(expr, term_dict, postings_file)
        return doc_ids


def _get_postings(term):
    return get_postings(term, term_dict, postings_file)


def _compute_rpn(expr):
    return compute_rpn(expr, term_dict, postings_file)


class SearchTestCase(unittest.TestCase):

    def test_and_operation(self):
        growth = _get_postings('growth')
        loss = _get_postings('loss')
        query = 'growth AND loss'
        expr = preprocess(query, term_dict)
        self.assertEqual([10067], _compute_rpn(expr))
        self.assertEqual(and_operation(growth, loss), _compute_rpn(expr))

    def test_not_operation(self):
        l_all = term_dict['ALL']['a']
        unions = _get_postings('unions')
        query = 'NOT unions'
        for elem in unions:
            l_all.remove(elem[0])
        expr = preprocess(query, term_dict)
        self.assertEqual(l_all, _compute_rpn(expr))
        self.assertEqual(not_operation(unions, term_dict['ALL']['a']), _compute_rpn(expr))

    def test_or_operation(self):
        t1 = 'their'
        t2 = 'final'
        l1 = _get_postings(t1)
        l2 = _get_postings(t2)
        query = t1 + ' OR ' + t2
        expr = preprocess(query, term_dict)
        self.assertEqual([1, 10005, 10041, 10043, 10048, 10062], _compute_rpn(expr))
        self.assertEqual(or_operation(l1, l2), _compute_rpn(expr))

    def test_operations(self):
        t0 = 'ALL'     # [1, 10, 100, 1000, 1003, 1007, 1008, 10000, 10002, 10005, 10008, 10011, 10014, 10015, 10018, 10023, 10025, 10027, 10032, 10035, 10037, 10038, 10040, 10041, 10042, 10043, 10046, 10048, 10049, 10050, 10052, 10053, 10054, 10057, 10058, 10061, 10062, 10064, 10065, 10066, 10067, 10068, 10071, 10073, 10074, 10075, 10076, 10078, 10079]
        t1 = 'the'     # [(1, 5), (10, 0), (100, 0), (1000, 0), (1008, 0), (10000, 10), (10002, 0), (10005, 0), (10011, 0), (10014, 0), (10015, 15), (10018, 0), (10025, 0), (10038, 0), (10041, 0), (10042, 20), (10043, 0), (10046, 0), (10048, 0), (10049, 0), (10052, 25), (10054, 0), (10057, 0), (10058, 0), (10062, 0), (10066, 30), (10067, 0), (10068, 0), (10071, 0), (10073, 0), (10078, 0)]
        t1_c = 'The'
        t2 = 'may'     # [(1, 2), (10054, 0), (10071, 4), (10073, 0), (10076, 0)]
        t2_c = 'mAy'
        t3 = 'end'     # [(1, 2), (10042, 0), (10062, 4), (10066, 0), (10071, 0)]

        query = '{}'.format(t3)
        self.assertEqual([1, 10042, 10062, 10066, 10071], main(query))
        # query = 'NOT {}'.format(t2)
        # self.assertEqual([10, 100, 1000, 1003, 1007, 1008, 10000, 10002, 10005, 10008, 10011, 10014, 10015, 10018, 10023, 10025, 10027, 10032, 10035, 10037, 10038, 10040, 10041, 10042, 10043, 10046, 10048, 10049, 10050, 10052, 10053, 10057, 10058, 10061, 10062, 10064, 10065, 10066, 10067, 10068, 10074, 10075, 10078, 10079], main(query))
        query = '{} AND {}'.format(t1_c, t2)
        self.assertEqual([1, 10054, 10071, 10073], main(query))
        query = '{} AND {}'.format(t1, t2_c)
        self.assertEqual([1, 10054, 10071, 10073], main(query))
        query = '{} OR {}'.format(t2, t3)
        self.assertEqual([1, 10042, 10054, 10062, 10066, 10071, 10073, 10076], main(query))
        query = '{} AND {} AND {}'.format(t1, t2, t3)
        self.assertEqual([1, 10071], main(query))
        query = '({} AND {}) AND {}'.format(t1, t2, t3)
        self.assertEqual([1, 10071], main(query))
        query = '{} AND ({} AND {})'.format(t1, t2, t3)
        self.assertEqual([1, 10071], main(query))
        query = '{} AND NOT {}'.format(t1, t2)
        self.assertEqual([10, 100, 1000, 1008, 10000, 10002, 10005, 10011, 10014, 10015, 10018, 10025, 10038, 10041, 10042, 10043, 10046, 10048, 10049, 10052, 10057, 10058, 10062, 10066, 10067, 10068, 10078], main(query))
        query = '{} AND NOT NOT {}'.format(t1, t2)
        self.assertEqual([1, 10054, 10071, 10073], main(query))
        query = '{} AND NOT NOT NOT {}'.format(t1, t2)
        self.assertEqual(
            [10, 100, 1000, 1008, 10000, 10002, 10005, 10011, 10014, 10015, 10018, 10025, 10038, 10041, 10042, 10043,
             10046, 10048, 10049, 10052, 10057, 10058, 10062, 10066, 10067, 10068, 10078], main(query))
        query = 'NOT {} AND {}'.format(t2, t1)
        self.assertEqual(
            [10, 100, 1000, 1008, 10000, 10002, 10005, 10011, 10014, 10015, 10018, 10025, 10038, 10041, 10042, 10043,
             10046, 10048, 10049, 10052, 10057, 10058, 10062, 10066, 10067, 10068, 10078], main(query))

        t4 = 'group'   # [(10018, 2), (10041, 0), (10052, 4), (10057, 0), (10078, 0)]
        t5 = 'march'   # [(1, 2), (1000, 0), (1003, 4), (10005, 0), (10078, 0)]
        t6 = 'american'# [(10027, 2), (10040, 0), (10049, 4), (10062, 0), (10064, 0)]
        t7 = 'also'    # [(1, 3), (10, 0), (1008, 0), (10014, 6), (10049, 0), (10054, 0), (10057, 0), (10066, 0), (10078, 0)]
        t8 = 'was'     # [(1, 3), (1000, 0), (10002, 0), (10005, 6), (10011, 0), (10014, 0), (10041, 0), (10049, 0), (10078, 0)]

        # query = 'NOT (a OR b AND c AND NOT d) AND NOT d AND (a OR b AND c)'
        query = 'NOT ({} OR {} AND {} AND NOT {}) AND ({} OR {} AND NOT {} AND {})'.format(t1, t2, t3, t4, t1, t2, t4, t3)
        self.assertEqual([], main(query))

        # query = 'nonexistingword AND NOT (a AND NOT b AND NOT c OR d OR c)'
        query = '{} AND NOT ({} AND NOT {} AND NOT {} OR {} OR {})'.format('nonexistingword', t1, t2, t3, t4, t3)
        self.assertEqual([], main(query))

        query = 'NOT ({} OR {} AND {} AND NOT {}) AND ({} OR {} AND NOT {} AND {}) OR ' \
                '{} AND NOT ({} AND NOT {} AND NOT {} OR {} OR {})'.format(t1, t2, t3, t4, t1, t2, t4, t3, 'nonexistingword', t1, t2, t3, t4, t3)

        self.assertEqual([], main(query))

        a = t1 = 'the'
        b = t2 = 'may'
        c = t3 = 'end'
        d = t4 = 'group'
        e = t5 = 'march'
        f = t6 = 'american'
        g = t7 = 'also'
        h = t8 = 'was'

        # NOT (a AND b AND NOT c AND d OR e AND f OR NOT b) AND (e AND f OR NOT b OR a AND NOT c AND d AND b) AND (NOT c AND e OR d AND NOT b AND c OR f)
        query = 'NOT (the AND may AND NOT end AND group OR march AND american OR NOT may) AND (march AND american OR NOT may OR the AND NOT end AND group AND may) ' \
                'AND (NOT the AND may OR was AND NOT march AND group OR end)'
        print query
        self.assertEqual([], main(query))

        query = 'NOT the AND the AND may'
        self.assertEqual([], main(query))

        #NOT (a AND b AND NOT c AND d OR e AND f OR NOT b) AND (e AND f OR NOT b OR a AND NOT c AND d AND b) AND (NOT c AND e OR d AND NOT b AND c OR f)
        query = 'NOT (the AND may AND NOT end AND group OR march AND american OR NOT may) AND (the AND may AND NOT end AND group OR march AND american OR NOT may) AND (NOT the AND may OR was AND NOT march AND group OR end)'
        self.assertEqual([], main(query))


        # NOT a AND a AND b AND NOT d AND e
        # NOT a AND a AND NOT d AND b AND e

        query = 'may AND may AND NOT the AND the AND NOT march AND march'
        self.assertEqual([], main(query))

        query = 'NOT the AND the AND NOT may AND march AND was'
        self.assertEqual([], main(query))

        query = 'the AND NOT the AND NOT may AND march AND was'
        print query
        self.assertEqual([], main(query))

        query = 'NOT the AND the'
        print query
        self.assertEqual([], main(query))

        query = 'the AND NOT the'
        print query
        self.assertEqual([], main(query))

        query = 'NOT march AND march OR the AND NOT the'
        print query
        self.assertEqual([], main(query))

        query = '(march AND NOT march) OR (the AND NOT the)'
        print query
        self.assertEqual([], main(query))

        query = '(march AND NOT march) OR (the AND NOT the)'
        print query
        self.assertEqual([], main(query))

        query = 'NOT {} AND {}'.format(t4, t5)
        self.assertEqual([1, 1000, 1003, 10005], main(query))
        query = '{} OR {} OR {}'.format(t4, t5, t6)
        self.assertEqual([1, 1000, 1003, 10005, 10018, 10027, 10040, 10041, 10049, 10052, 10057, 10062, 10064, 10078], main(query))
        query = '{} AND {} OR {}'.format(t4, t5, t6)
        self.assertEqual([10027, 10040, 10049, 10062, 10064, 10078], main(query))

        query = 'NOT ({} AND {}) AND ({} AND {}) AND {}'.format(
            t1, t2, t1, t2, t3
        )
        self.assertEqual([], main(query))

        query = 'the AND NOT the AND NOT may AND march'
        print main(query)


        query = 'NOT the AND the'
        self.assertEqual([], main(query))
        query = 'NOT the AND the AND may'
        self.assertEqual([], main(query))
        query = 'NOT group AND group AND march'
        self.assertEqual([], main(query))

        query = 'NOT group AND group AND NOT (group AND march)'
        self.assertEqual([], main(query))


if __name__ == '__main__':
    unittest.main()
