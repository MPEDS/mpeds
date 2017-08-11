
from mpeds.classify_protest import MPEDS
from mpeds.parsers.lexisnexis import parseLexisNexis

import pandas as pd
import numpy as np

from pkg_resources import resource_filename

from hashlib import md5

def pubToID(pubname):
    return "-".join(pubname.split())

articles = parseLexisNexis(resource_filename(__name__, 'documents/University_Wire2012-01-01_2012-01-31.TXT'))
df = pd.DataFrame(articles)

## generate ID based on publication, date, and hash of text of document
df['id'] = df.apply(lambda x: "%s_%s_%s" % (pubToID(x['PUBLICATION']), x['DATE'], md5(x['TEXT']).hexdigest()), axis = 1)

## drop duplicates based on ID
df = df.drop_duplicates('id')

## create MPEDS object
mobj = MPEDS()
df['y'] = mobj.haystack(df['TEXT'])

## select only those events which contain protest events
df_protest = df[df['y'] == 1]

df_protest['form'] = mobj.getForm(df_protest['TEXT'])
df_protest['issue'] = mobj.getIssue(df_protest['TEXT'])
df_protest['target'] = mobj.getTarget(df_protest['TEXT'])

df_protest['size'] = mobj.getSize(df_protest['TEXT'])
df_protest['smo'] = mobj.getSMO(df_protest['TEXT'])

df_protest['location'] = mobj.getLocation(df_protest['TEXT'])

## output to file
df_protest[['id', 'TITLE', 'DATE', 'PUBLICATION', 'form', 'issue', 'target', 'size', 'smo', 'location']].\
    to_csv('mpeds-output.csv', encoding = 'utf-8')
print("Output saved to mpeds-output.csv.")