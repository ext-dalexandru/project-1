"""Spacy code refactored from the notebook
"""
# from collections import OrderedDict
from collections import Counter
from functools import reduce
import json
# import os
import re

from tqdm import tqdm
tqdm.pandas()

import pandas as pd

import spacy
nlp = spacy.load('en_core_web_sm')
# from textpipe import doc
from sklearn.feature_extraction.text import TfidfVectorizer


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

def clean_tags(html_body):
    """Text cleaning function.

    :param html_body: text as html/pseudo-html body
    :return: string
    """
    # textpipe alternative
    # html_body = doc.Doc(html_body).clean

    # TODO: make it faster
    html_body = html_body.strip()
    html_body = re.sub('<[^<]+?>', '', html_body).strip()
    html_body = re.sub('<[^>]*(>|$)|&nbsp;|&zwnj;|&amp;|&raquo;|&laquo;|&gt', ' ', html_body)
    html_body = re.sub('\s+', ' ', html_body).strip() # TODO: check in Pythex
    html_tokens = [p for p in html_body.split(" ") if len(p) <= 46]

    html_body = " ".join(html_tokens)
    html_body = str(html_body.encode('ascii', errors='ignore'))
    html_body = re.sub('\s+', ' ', html_body).strip() # TODO: check in Pythex
    html_body = re.sub('\\*r', '', html_body).strip()
    html_body = re.sub('\\*n', '', html_body).strip()
    html_body = re.sub('\\*t', '', html_body).strip()
    html_body = re.sub('\\*', '', html_body).strip()

    if html_body.startswith("b'") and html_body.endswith("'"):
        html_body = html_body[2:-3]

    return str(html_body)

def lemmatization(text, allowed_postags=('NOUN', 'PROPN')):
    """Lemmatizes given text -> breaks text into words, for each word it extracts the root / lemma

    :param text: given text
    :param allowed_postags: allowed part-of-speech (POS) tags, to be returned in the final result
    :return: texts_out
    """
    doc = nlp(text)
    texts_out = [token.lemma_.lower() for token in doc if token.pos_ in allowed_postags]
    return texts_out

# ----------------------------------------------------------------------------
def generate_datasets(df):
    """Generate datasets based on raw data.

    :param df: raw data
    """
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
    # df = df[:50]

    print('Running clean_tags(): ')
    df['Description_clean'] = df.Description.progress_apply(clean_tags)

    print('Running lemmatization(): ')
    df['Description_lemmatized'] = df.Description_clean.progress_apply(lemmatization)

    print('Running Counter(): ')
    df['Description_lemmatized_wc'] = df.Description_lemmatized.progress_apply(Counter)

    # TODO: V1 artifacts
    # print('Running running_counter(): ')
    # running_counter(associations['Administrative Assistant'])

    print('Reduce to global counter for each title: ')
    data = df[df.Query_word_len == 2].Query.unique()

    for title in data:
        # tf-idf datasets
        tfIdfVectorizer = TfidfVectorizer(use_idf=True)
        tfIdf = tfIdfVectorizer.fit_transform(df[df.Query == title].Description_clean)

        df_tf = pd.DataFrame(
            tfIdf[0].T.todense(),
            index=tfIdfVectorizer.get_feature_names(),
            columns=["TF-IDF"]
        )
        df_tf = df_tf.reset_index(level=0)
        df_tf = df_tf.rename(columns={'index': 'term', 'TF-IDF': 'tfidf_score'})

        df_tf = df_tf[df_tf.tfidf_score > 0]
        df_tf = df_tf.sort_values('tfidf_score', ascending=False)
        df_tf.to_csv(f'../data/processed/descriptions_tfidf/tf_{title}.csv', index=False)

        # counter datasets
        result = reduce(
            lambda l1, l2: l1 + l2,
            tqdm(
                df[df.Query == title] \
                    .Description_lemmatized_wc.values
            )
        )
        df_result = pd.DataFrame.from_dict(result, orient='index').reset_index()
        df_result = df_result.rename(columns={'index': 'term', 0: 'freq'})

        df_result = df_result[df_result.freq >= 5]
        df_result = df_result.sort_values('freq', ascending=False)
        df_result.to_csv(f'../data/processed/descriptions_global_counter/ncount_{title}.csv', index=False)

        # json.dump(
        #     OrderedDict(result.most_common()),
        #     open(f'../data/processed/descriptions_global_counter/nouns_count_{title}.json', 'w')
        # )


if __name__ == '__main__':
    # data_source = os.path.join(os.getcwd(), 'data/raw/bman93_job/Top30.csv')
    # df = pd.read_csv(data_source)
    df = pd.read_csv('../data/raw/bman93_job/Top30.csv')
    generate_datasets(df)
    
