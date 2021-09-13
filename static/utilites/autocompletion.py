import copy
import re
import itertools
from typing import List, Dict, Optional, Iterator
from flask import url_for


class Autocompleter(object):
    def __init__(self, phenos):
        """
        :param phenos: a dictionary of phecodes to phenotypes
        :param variants: a tuple of
        """
        self._phenos = copy.deepcopy(phenos)
        self._preprocess_phenos()
        self._autocompleters = [
            # self._autocomplete_rsid,  # Check rsid first, because it only runs if query.startswith('rs')
            # self._autocomplete_variant,  # Check variant next, because it only runs if query starts with a chrom alias.
            self._autocomplete_phenocode
        ]
        if any('phenostring' in pheno for pheno in self._phenos.values()):
            self._autocompleters.append(self._autocomplete_phenostring)

    def autocomplete(self, query: str) -> List[Dict[str, str]]:
        query = query.strip()
        result = []
        for autocompleter in self._autocompleters:
            result = list(itertools.islice(autocompleter(query), 0, 10))
            if result:
                break
        return result

    def get_best_completion(self, query: str) -> Optional[Dict[str, str]]:

        suggestions = self.autocomplete(query)
        if not suggestions:
            return None
        query_tokens = query.strip().lower().split()
        return max(suggestions, key=lambda sugg: self._get_suggestion_quality(query_tokens, sugg['display']))

    def _get_suggestion_quality(self, query_tokens: List[str], display: str) -> float:
        suggestion_tokens = display.lower().split()
        intersection_tokens = set(query_tokens).intersection(suggestion_tokens)
        return len(intersection_tokens) / len(suggestion_tokens)

    _process_string_non_word_regex = re.compile(r"(?ui)[^\w\.]")  # Most of the time we want to include periods in words
    @classmethod
    def _process_string(cls, string: str) -> str:
        # Cleaning inspired by <https://github.com/seatgeek/fuzzywuzzy/blob/6353e2/fuzzywuzzy/utils.py#L69>
        return ' ' + cls._process_string_non_word_regex.sub(' ', string).lower().strip()

    def _preprocess_phenos(self) -> None:
        for phenocode, pheno in self._phenos.items():
            pheno['--spaced--phenocode'] = self._process_string(phenocode)
            if 'phenostring' in pheno:
                pheno['--spaced--phenostring'] = self._process_string(pheno['phenostring'])

    def _autocomplete_phenocode(self, query: str) -> Iterator[Dict[str, str]]:
        query = self._process_string(query)
        for phenocode, pheno in self._phenos.items():
            if query in pheno['--spaced--phenocode']:
                yield {
                    "value": phenocode,
                    "display": "{} ({})".format(phenocode,
                                                pheno['phenostring']) if 'phenostring' in pheno else phenocode,

                    "url": url_for('.phenotype_page', pheno=phenocode),
                }

    def _autocomplete_phenostring(self, query: str) -> Iterator[Dict[str, str]]:
        query = self._process_string(query)
        for phenocode, pheno in self._phenos.items():
            if query in pheno['--spaced--phenostring']:
                yield {
                    "value": phenocode,
                    "display": "{} ({})".format(pheno['phenostring'], phenocode),
                    "url": url_for('.phenotype_page', pheno=phenocode),
                }

    def _autocomplete_variant(self, query: str):
        query = query.replace('-', ':')
        split_query = query.split(':')
        chrom, pos, ref, alt = [split_query[i] for i in range(0, 4)]
