"""Spacy code refactored from the notebook
"""
from collections import Counter
from functools import reduce
import json
# import os

from tqdm import tqdm
tqdm.pandas()

import pandas as pd

import spacy
nlp = spacy.load('en_core_web_sm')


def check_associations(association, elem_a, elem_b):
    """Check if association pair is in dictionary

    :param association: association dictionary
    :param elem_a: first element
    :param elem_b: second element
    :return: associations

    ..doctest::
        >>> test = {'A': ['B']}
        >>> check_associations(test, 'A', 'C')
        {'A': ['B', 'C']}
        >>> test = {'A': ['B']}
        >>> check_associations(test, 'B', 'A')
        {'A': ['B'], 'B': ['A']}
    """

    if elem_a not in association:
        association[elem_a] = []

    if elem_b not in association[elem_a]:
        association[elem_a].append(elem_b)

    return association


def title_associations(df_slice, title_column_name, symmetric=False):
    """Split job titles, build an association dictionary (taxonomy)

    :param df_slice: slice of the dataframe used (preferred over full dataframe)
    :param title_column_name: name of the job title column
    :param symmetric: symmetric associations (eg: "A B" -> "A->B", "B->A")
    :return: associations
    ..doctest::
        >>> print('TODO')
        TODO
    """
    series = df_slice[title_column_name].str.split()

    associations = {}
    for row in series:
        elem_a = row[0]
        elem_b = row[1]

        # TODO: Clean, but inefficient ? (pass by reference is useful for larger dict)
        check_associations(associations, elem_a, elem_b)

        if symmetric:
            check_associations(associations, elem_b, elem_a)

    return associations


def lemmatization(text, allowed_postags=['NOUN', 'PROPN', 'ADJ']):
    doc = nlp(text)
    texts_out = [token.lemma_.lower() for token in doc if token.pos_ in allowed_postags]
    return texts_out


def running_counter(associations, job_title):
    # running = Counter()
    # for cnter in associations[job_title]:
    #     running += Counter(cnter)

    # return running
    pass

if __name__ == '__main__':
    # data_source = os.path.join(os.getcwd(), 'data/raw/bman93_job/Top30.csv')
    # df = pd.read_csv(data_source)
    df = pd.read_csv('../data/raw/bman93_job/Top30.csv')

    # ================== ETL ===================================================
    df['Query_split'] = df.Query.str.split()
    df['Query_word_len'] = df.Query_split.apply(len)

    # ================== Title Associations ====================================
    print('Running title_associations(): ')
    # 2 or 3-word titles contain just the title, not "full-time", "remote" etc
    data = df[df.Query_word_len == 2]
    t_assoc = title_associations(data, 'Query')
    t_assoc_sym = title_associations(data, 'Query', symmetric=True)

    print('Saving title associations ...')
    json.dump(t_assoc, open('../data/processed/job_title_association.json', 'w'))
    json.dump(t_assoc_sym, open('../data/processed/job_title_association_sym.json', 'w'))

    # ================== Keyword association ===================================
    # Time issues
    df = df[:50]

    print('Running lemmatization(): ')
    df['Description_lemmatized'] = df.Description.progress_apply(lemmatization)

    print('Running Counter(): ')
    df['Description_lemmatized_wc'] = df.Description_lemmatized.progress_apply(Counter)

    # TODO: V1 artifacts
    # print('Running running_counter(): ')
    # running_counter(associations['Administrative Assistant'])

    print('Reduce to global counter for each title: ')
    data = df[df.Query_word_len == 2].Query.unique()

    for title in data:
        result = reduce(
            lambda l1, l2: l1 + l2,
            tqdm(
                df[df.Query == title]\
                    .Description_lemmatized_wc.values
            )
        )
        # print(result)

        json.dump(result, open(f'../data/processed/titles_global_counter/nouns_count_{title}.json', 'w'))