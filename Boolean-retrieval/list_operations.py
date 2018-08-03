"""
    File name: list_operations.py
    Authors: Svilen Stefanov and Wang Chin-Hao
    Date created: 15/02/2018
    Date last modified: 04/03/2018
    Python Version: 2.7
"""

def and_operation(l1, l2):
    """
    Create a list of all elements that are common for both lists.
    :param l1: the first list that is part of the merge
    :param l2: the second list that is part of the merge
    :return: the result after applying the AND merge on the two lists
    """
    l1_len = len(l1)
    l2_len = len(l2)
    ans = []
    if l1_len == 0 or l2_len == 0:
        return ans
    p1 = p2 = 0
    while p1 < l1_len and p2 < l2_len:
        l1_doc_id = l1[p1][0] if type(l1[p1]) == tuple else l1[p1]
        l2_doc_id = l2[p2][0] if type(l2[p2]) == tuple else l2[p2]
        if l1_doc_id == l2_doc_id:
            ans.append(l1_doc_id)
            p1 += 1
            p2 += 1
        elif l1_doc_id < l2_doc_id:
            # check if element is a tuple, has skip pointer, and the doc_id skip pointer points to is <= l2_doc_id
            while type(l1[p1]) == tuple and l1[p1][1] and l1[l1[p1][1]][0] <= l2_doc_id:
                p1 = l1[p1][1]
            l1_doc_id = l1[p1][0] if type(l1[p1]) == tuple else l1[p1]
            if l1_doc_id != l2_doc_id:
                p1 += 1
        else:
            while type(l2[p2]) == tuple and l2[p2][1] and l2[l2[p2][1]][0] <= l1_doc_id:
                p2 = l2[p2][1]
            l2_doc_id = l2[p2][0] if type(l2[p2]) == tuple else l2[p2]
            if l2_doc_id != l1_doc_id:
                p2 += 1
    return ans


def or_operation(l1, l2):
    """
    Return a list of all elements that are to be seen in l1 or l2.
    :param l1: the first list that is part of the merge
    :param l2: the second list that is part of the merge
    :return: the result after applying the OR merge on the two lists
    """
    ans = []
    l1_len = len(l1)
    l2_len = len(l2)
    if l1_len == 0 and l2_len == 0:
        return ans
    elif l1_len == 0:
        return [x[0] for x in l2] if type(l2[0]) == tuple else l2
    elif l2_len == 0:
        return [x[0] for x in l1] if type(l1[0]) == tuple else l1
    p1 = p2 = 0
    while p1 < l1_len and p2 < l2_len:
        l1_doc_id = l1[p1][0] if type(l1[p1]) == tuple else l1[p1]
        l2_doc_id = l2[p2][0] if type(l2[p2]) == tuple else l2[p2]
        if l1_doc_id == l2_doc_id:
            ans.append(l2_doc_id)
            p1 += 1
            p2 += 1
        elif l1_doc_id < l2_doc_id:
            ans.append(l1_doc_id)
            p1 += 1
        else:
            ans.append(l2_doc_id)
            p2 += 1
    while p1 < l1_len:
        l1_doc_id = l1[p1][0] if type(l1[p1]) == tuple else l1[p1]
        ans.append(l1_doc_id)
        p1 += 1
    while p2 < l2_len:
        l2_doc_id = l2[p2][0] if type(l2[p2]) == tuple else l2[p2]
        ans.append(l2_doc_id)
        p2 += 1
    return ans


def not_operation(l, l_all):
    """
    Return a list of all elements from the training data set that are not in l.
    :param l: the list which negation is to be found (all document IDs without these in this list)
    :param l_all: list of all document IDs part of the training data set
    :return: all docIDs that are not in l
    """
    ans = []
    l_len = len(l)
    all_len = len(l_all)
    if l_len == 0:
        return l_all
    p = pa = 0
    while p < l_len and pa < all_len:
        l_doc_id = l[p][0] if type(l[p]) == tuple else l[p]
        if l_doc_id == l_all[pa]:
            p += 1
            pa += 1
        else:
            ans.append(l_all[pa])
            pa += 1

    while pa < all_len:
        ans.append(l_all[pa])
        pa += 1
    return ans


def and_not_operation(l1, l2, l_all):
    """
    Return a list that contain all elements in l1 that are disjunkt from the elements in l2.
    :param l1: the first list that is part of the merge
    :param l2: the second list that is part of the merge
    :param l_all: list of all document IDs part of the training data set
    :return: the result after applying the AND NOT merge on the two lists
    """
    ans = []
    l1_len = len(l1)
    l2_len = len(l2)
    if l1_len == 0:
        return ans
    elif l2_len == 0:
        return and_operation(l1, l_all)
    p1 = p2 = 0
    while p1 < l1_len and p2 < l2_len:
        l1_doc_id = l1[p1][0] if type(l1[p1]) == tuple else l1[p1]
        l2_doc_id = l2[p2][0] if type(l2[p2]) == tuple else l2[p2]
        if l1_doc_id < l2_doc_id:
            ans.append(l1_doc_id)
            p1 += 1
        elif l1_doc_id > l2_doc_id:
            p2 += 1
        else:   # l1_doc_id == l2_doc_id:
            p1 += 1
            p2 += 1
    while p1 < l1_len:
        l1_doc_id = l1[p1][0] if type(l1[p1]) == tuple else l1[p1]
        ans.append(l1_doc_id)
        p1 += 1
    return ans
