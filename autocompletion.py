import copy


class Autocompleter(object):
    def __init__(self, phenos):
        self_phenos = copy.deepcopy(phenos)