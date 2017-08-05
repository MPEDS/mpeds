.. highlight:: rst
.. module:: mpeds.classify_protest


MPEDS is an automated tool for extracting protest event data from news articles.


Haystack classification
=======================

The first task is to identify whether a news article contains information about a protest event. This is a binary classification task, and it is performed by an ensemble of classification models.

The haystack classifier method is called with the ``haystack`` method, and will return a pandas series of predictions. 1 corresponds to a predicted protest, while 0 means the article is not predicted to contain information on a protest event.

.. autoclass:: mpeds.classify_protest.MPEDS
   :members: haystack
   
   
Closed-ended classifiers
========================

In addition to classifying whether a news article describes a protest or not, MPEDS extracts information about the nature of the protest.

Form
----

.. autoclass:: mpeds.classify_protest.MPEDS
   :members: getForm, getFormProb

