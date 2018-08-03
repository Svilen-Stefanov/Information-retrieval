import unittest
from preprocess import preprocess_andnot, reorder_based_on_size, eval_expr_size, preprocess

"""
    File name: test_preprocess.py
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 06/03/2018
    Python Version: 2.7
"""

class PreprocessAndNotTestCase(unittest.TestCase):
    """Tests for preprocess_andnot in `preprocess.py`."""
    def test_not_and_convert_to_and_not(self):
        self.assertEqual('Gates AND NOT Bill', preprocess_andnot('NOT Bill AND Gates'))
        self.assertEqual('gates AND NOT Bill', preprocess_andnot('NOT Bill AND gates'))
        self.assertEqual('Steve AND NOT Bill AND NOT Jobs AND NOT Apple',
                         preprocess_andnot('NOT Bill AND Steve AND NOT Jobs AND NOT Apple'))
        self.assertEqual('Steve OR Apple AND NOT Jobs AND NOT Gates OR ( Facebook AND NOT Amazon OR Reddit OR NOT Google )',
                         preprocess_andnot('Steve OR NOT Jobs AND Apple AND NOT Gates OR ( NOT Amazon AND Facebook OR Reddit OR NOT Google )'))

    def test_no_convert(self):
        self.assertEqual('NOT Gates AND NOT Bill', preprocess_andnot('NOT Gates AND NOT Bill'))
        self.assertEqual('NOT ( Gates AND NOT Bill )', preprocess_andnot('NOT ( Gates AND NOT Bill )'))
        self.assertEqual('NOT ( Apple AND Google )', preprocess_andnot('NOT ( Apple AND Google )'))
        self.assertEqual('Bill OR Steve AND ( Jobs AND NOT Apple )',
                         preprocess_andnot('Bill OR Steve AND ( Jobs AND NOT Apple )'))
        self.assertEqual('Bill AND NOT Steve AND NOT Jobs AND NOT Apple',
                         preprocess_andnot('Bill AND NOT Steve AND NOT Jobs AND NOT Apple'))
        self.assertEqual('NOT Bill AND NOT Steve AND NOT Apple',
                         preprocess_andnot('NOT Bill AND NOT Steve AND NOT Apple'))
        self.assertEqual(
            'NOT ( bill AND gates ) AND NOT ( steve OR NOT jobs ) OR ( NOT Apple AND NOT Google AND NOT Facebook ) OR NOT Amazon',
            preprocess_andnot(
                'NOT ( bill AND gates ) AND NOT ( steve OR NOT jobs ) OR ( NOT Apple AND NOT Google AND NOT Facebook ) OR NOT Amazon'))
        self.assertEqual('Bill OR Gates AND Oscar OR Apple AND NOT Svilen OR Microsoft AND NOT ( Azzure AND Pi )',
                         preprocess_andnot('Bill OR Gates AND Oscar OR NOT Svilen AND Apple OR NOT ( Azzure AND Pi ) AND Microsoft'))


class ReoroderBasedOnSizeTestCase(unittest.TestCase):

    term_dict1 = {
        'ALL': {'f': 150},
        'one': {'f': 1}, 'two': {'f': 2}, 'three': {'f': 3}, 'four': {'f': 4}, 'five': {'f': 5},
        'six': {'f': 6}, 'seven': {'f': 7}, 'eight': {'f': 8}, 'nine': {'f': 9}, 'twenty': {'f': 20},
        'hundred': {'f': 100}
    }

    term_dict2 = {
        'ALL': {'f': 100},
        'two': {'f': 2}, 'four': {'f': 4}, 'six': {'f': 6}, 'eight': {'f': 8}, 'ten': {'f': 10},
        'hundred': {'f': 100}
    }

    def test(self):
        self.assertEqual('two AND four', reorder_based_on_size('four AND two', self.term_dict1))
        self.assertEqual('two AND four OR hundred', reorder_based_on_size('four AND two OR hundred', self.term_dict1))
        self.assertEqual('( three AND hundred ) OR two AND four', reorder_based_on_size('( hundred AND three ) OR four AND two', self.term_dict1))


class EvalExprSizeTestCase(unittest.TestCase):

    term_dict1 = {
        'ALL': {'f': 150},
        'one': {'f': 1}, 'two': {'f': 2}, 'three': {'f': 3}, 'four': {'f': 4}, 'five': {'f': 5},
        'six': {'f': 6}, 'seven': {'f': 7}, 'eight': {'f': 8}, 'twenty': {'f': 20},
        'hundred': {'f': 100}
    }

    term_dict2 = {
        'ALL': {'f': 100},
        'two': {'f': 2}, 'four': {'f': 4}, 'six': {'f': 6}, 'eight': {'f': 8}, 'ten': {'f': 10},
        'hundred': {'f': 100}
    }

    def test_one_word(self):
        terms = ['one', 'four', 'seven', 'hundred']
        for term in terms:
            self.assertEqual(self.term_dict1[term]['f'], eval_expr_size(term, self.term_dict1))

    def test_not(self):
        terms = ['one', 'four', 'seven', 'hundred']
        for term in terms:
            self.assertEqual(self.term_dict1['ALL']['f'] - self.term_dict1[term]['f'],
                             eval_expr_size('NOT ' + term, self.term_dict1))

    def test_parenthesis_term_dict1(self):
        self.assertEqual(2, eval_expr_size('( two AND seven )', self.term_dict1))
        self.assertEqual(9, eval_expr_size('( two OR seven )', self.term_dict1))
        self.assertEqual(100, eval_expr_size('( hundred AND NOT two )', self.term_dict1))
        self.assertEqual(8, eval_expr_size('( one AND hundred OR seven AND NOT two )', self.term_dict1))

    def test_parenthesis_term_dict2(self):
        self.assertEqual(98, eval_expr_size('( hundred AND NOT two )', self.term_dict2))
        self.assertEqual(0, eval_expr_size('( NOT two AND NOT hundred )', self.term_dict2))
        self.assertEqual(4, eval_expr_size('( NOT two AND NOT hundred OR four )', self.term_dict2))
        self.assertEqual(16, eval_expr_size('( four OR NOT eight AND two OR ten )', self.term_dict2))


class ReoroderBasedOnSizeTestCase(unittest.TestCase):

    term_dict1 = {
        'ALL': {'f': 150},
        'one': {'f': 1}, 'two': {'f': 2}, 'three': {'f': 3}, 'four': {'f': 4}, 'five': {'f': 5},
        'six': {'f': 6}, 'seven': {'f': 7}, 'eight': {'f': 8}, 'nine': {'f': 9}, 'twenty': {'f': 20},
        'hundred': {'f': 100}
    }

    term_dict2 = {
        'ALL': {'f': 100},
        'two': {'f': 2}, 'four': {'f': 4}, 'six': {'f': 6}, 'eight': {'f': 8}, 'ten': {'f': 10},
        'hundred': {'f': 100}
    }

    def test(self):
        self.assertEqual('four AND two', reorder_based_on_size('four AND two', self.term_dict1))
        self.assertEqual('four AND two OR hundred', reorder_based_on_size('four AND two OR hundred', self.term_dict1))
        self.assertEqual('( hundred AND three ) OR four AND two', reorder_based_on_size('( hundred AND three ) OR four AND two', self.term_dict1))
        self.assertEqual('NOT ( four AND two ) OR NOT ( NOT nine AND six ) OR hundred AND twenty',
                        reorder_based_on_size('NOT ( four AND two ) OR NOT ( six AND NOT nine ) OR hundred AND twenty', self.term_dict1))

if __name__ == '__main__':
    unittest.main()
