"""Spacy code refactored from the notebook
"""
import json
import pandas as pd

import spacy
nlp = spacy.load('en_core_web_sm')


def title_associations(df_slice, title_column_name):
    series = df_slice[title_column_name].str.split()

    associations = {}
    for row in series.itertuples():
        elem_a = row[0]
        elem_b = row[1]

        if elem_a in associations:
            if elem_b in associations[elem_a]:
                pass
            else:
                associations[elem_a].append(elem_b)
        else:
            associations[elem_a] = []

    return associations


if __name__ == '__main__':
    df = pd.read_csv('')

    print('Running title_associations(): ')
    t_assoc = title_associations(df[df.Query_word_len == 2], 'Query')

    print('Saving title associations ...')
    json.dump(t_assoc, open('../data/processed/job_title_association.json', 'w'))
