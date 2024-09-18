from itertools import zip_longest

from deepmerge import Merger


def lists_merge_index(ls1, ls2):
  return [n2 if None != n2 else n1 for n1, n2 in zip_longest(ls1, ls2, fillvalue = None)]

def merge_strategy_list_extend(config, path, node, nxt):
  return lists_merge_index(node, nxt)

dict_deepmerger_extend_lists = Merger(
    # pass in a list of tuple, with the
    # strategies you are looking to apply
    # to each type.
    [
        (list, merge_strategy_list_extend),
        (dict, ["merge"]),
        (set, ["union"])
    ],
    # next, choose the fallback strategies,
    # applied to all other types:
    ["override"],
    # finally, choose the strategies in
    # the case where the types conflict:
    ["override"]
)

