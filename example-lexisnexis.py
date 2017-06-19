
from mpeds.classify_protest import MPEDS
from mpeds.parsers.lexisnexis import parseLexisNexis

import pandas as pd
import numpy as np

from hashlib import md5

def pubToID(pubname):
    return "-".join(pubname.split())

articles = parseLexisNexis('documents/University_Wire2012-01-01_2012-01-31.TXT')
df = pd.DataFrame(articles)

## generate ID based on publication, date, and hash of text of document
df['id'] = df.apply(lambda x: "%s_%s_%s" % (pubToID(x['PUBLICATION']), x['DATE'], md5(x['TEXT']).hexdigest()), axis = 1)

## drop duplicates based on ID
df = df.drop_duplicates('id')

## create MPEDS object
mobj = MPEDS()
df['y'] = mobj.haystack(df['TEXT'])

## create dataframe which match protest
df_protest = df[df['y'] == 1]

## Error, not able to retrieve self.form_clf.classes_
## TK: Need to associate classes with this correctly
df_protest['form'] = mobj.getForm(df_protest['TEXT'])
df_protest['issue'] = mobj.getIssue(df_protest['TEXT'])
df_protest['target'] = mobj.getTarget(df_protest['TEXT'])

df_protest['size'] = mobj.getSize(df_protest['TEXT'])
df_protest['location'] = mobj.getLocation(df_protest['TEXT'])
df_protest['smo'] = mobj.getSMO(df_protest['TEXT'])