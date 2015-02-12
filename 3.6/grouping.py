__author__ = 'grzegorz'

import itertools


def group_values(values):

    if len(values) == 1:
        return [values]

    else:
        groups = []

        group = []
        i = 0
        while i < len(values)-1:
            while(values[i+1]-values[i] == 1):
                group.append(values[i+1])
                group.append(values[i])

                i += 1
                if i == len(values)-1:
                    break

            group = list(set(group))
            group.sort()
            groups.append(group)
            group = []
            i += 1

        #for each single value add another group
        groups_flatten = list(itertools.chain.from_iterable(groups))
        not_used = [item for item in values if item not in groups_flatten]
        for item in not_used:
            groups.append([item])

        #remove empty groups
        groups = [item for item in groups if len(item) > 0]
        return groups