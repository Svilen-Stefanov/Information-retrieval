import unittest
from reverse_polish_notation import rpn

"""
    File name: test_reverse_polish_notation.py
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 07/03/2018
    Python Version: 2.7
"""

class RpnTest(unittest.TestCase):

    def test_prefix_to_postfix(self):
        self.assertEqual(['him', 'me', 'AND'], rpn('him AND me'))
        self.assertEqual(['him', 'me', 'OR'], rpn('him OR me'))
        self.assertEqual(['me', 'NOT'], rpn('NOT me'))
        self.assertEqual(['bill', 'Gates', 'vista', 'XP', 'OR', 'mac', 'ANDNOT', 'AND', 'OR'],
                         rpn('bill OR Gates AND ( vista OR XP ) AND NOT mac'))
        print rpn('B OR C AND D')
        print rpn('C AND B AND A')

        self.assertEqual(['Bill', 'NOT', 'Gates', 'ANDNOT', 'PC', 'ANDNOT'], rpn('NOT Bill AND NOT Gates AND NOT PC'))
        self.assertEqual(['bill', 'gates', 'AND', 'NOT', 'steve', 'jobs', 'NOT', 'OR', 'ANDNOT',
                          'Apple', 'NOT', 'Google', 'ANDNOT', 'Facebook', 'ANDNOT', 'OR', 'Amazon', 'NOT', 'OR'],
                         rpn('NOT ( bill AND gates ) AND NOT ( steve OR NOT jobs ) OR ( NOT Apple AND NOT Google AND NOT Facebook ) OR NOT Amazon'))

        print rpn('NOT ( A AND B ) AND C')


if __name__ == '__main__':
    unittest.main()
