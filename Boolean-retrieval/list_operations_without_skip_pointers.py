"""
    File name: list_operations_without_skip_pointers.py
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 05/03/2018
    Python Version: 2.7
"""

def not_operation(l, all):
    # TODO: FOR NOW - change 'all' as a global variable containing all postings
    # TODO: Consider storing length of all postings in dict.txt?
    ans = []
    p = pa = 0
    l_len = len(l)
    all_len = len(all)
    while p < l_len and pa < all_len:
        if l[p][0] == all[pa]:
            p += 1
            pa += 1
        else:
            ans.append(all[pa])
            pa += 1

    while pa < all_len:
        ans.append(all[pa])
        pa += 1
    return ans


def or_operation(l1, l2):
    l = []
    while l1 and l2:
        if l1[0] < l2[0]:
            l.append(l1.pop(0))
        else:
            l.append(l2.pop(0))
    return l + l1 + l2


def and_not_operation(l1, l2):
    # TODO Consider using for p1 in l1_len and p2 in l2_len ?
    ans = []
    p1 = p2 = 0
    l1_len = len(l1)
    l2_len = len(l2)
    while p1 < l1_len and p2 < l2_len:
        if l1[p1] < l2[p2]:
            ans.append(l1[p1])
            p1 += 1
        elif l1[p1] > l2[p2]:
            p2 += 1
        else:   # l1[p1] == l2[p2]
            p1 += 1
            p2 += 1
    while p1 < l1_len:
        ans.append(l1[p1])
        p1 += 1
    return ans


def and_operation(l1, l2):
    ans = []
    p1 = p2 = 0
    l1_len = len(l1)
    l2_len = len(l2)
    while p1 < l1_len and p2 < l2_len:
        if l1[p1] == l2[p2]:
            ans.append(l1[p1])
            p1 += 1
            p2 += 1
        elif l1[p1] < l2[p2]:
            p1 += 1
        else:
            p2 += 1
    return ans
