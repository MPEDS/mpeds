from distutils.core import setup

setup(
    name='MPEDS',
    packages=['mpeds'],
    data_files=[('tokenizers', ['tokenizers/stanford-ner-3.6.0-javadoc.jar', 'tokenizers/stanford-ner-3.6.0-sources.jar', 'tokenizers/stanford-ner-3.6.0.jar']),
        ('classifiers', ['classifiers/form-vect_2017-05-23.pkl', 'classifiers/form_2017-05-23.pkl', 'classifiers/haystack-vect_all-source_2017-05-24.pkl', 'classifiers/haystack_all-source_2017-05-24.pkl', 'classifiers/issue-vect_2017-05-23.pkl', 'classifiers/issue_2017-05-23.pkl', 'classifiers/ner-orgs_2016-03-28_all.ser.gz', 'classifiers/target-vect_2017-06-27.pkl', 'classifiers/target_2017-06-27.pkl'])
        ]
    )
