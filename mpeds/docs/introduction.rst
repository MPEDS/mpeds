.. highlight:: rst
.. module:: mpeds.classify_protest


MPEDS is an automated tool for extracting protest event data from news articles. It consists of three tasks: identification of news articles that describe a protest event (haystack classification); classification of protest form, target, and issue (closed-ended coding task); and extraction of size, social movement organizations, and location (open-ended coding task).


Haystack classification
=======================

The first task is to identify whether a news article contains information about a protest event. This is a binary classification task, and it is performed by an ensemble of classification models.

The haystack classifier method is called with the ``haystack`` method, and will return a pandas series of predictions. 1 corresponds to a predicted protest, while 0 means the article is not predicted to contain information on a protest event.

.. autoclass:: mpeds.classify_protest.MPEDS
   :members: haystack


Closed-ended classifiers
========================

In addition to classifying whether a news article describes a protest or not, MPEDS extracts information about the nature of the protest. These additional variables take two main forms: closed-ended variables that can take on one of a discrete number of values, while open-ended variables can take any number of values.

There are three closed-ended classification tasks: the form, issue, and target of the protest. For each of these, MPEDS both predicts a class and returns probability estimates associated with all of the classes.

Form
----

There are 11 possible values for the form of the protest: *Blockade/slowdown/disruption, Boycott, Hunger Strike, March, Occupation/sit-in, Rally/demonstration, Rally/demonstration-March, Riot, Strike/walkout/lockout, Symbolic display/symbolic action*, and *None*. A logistic regression classifier is used to predict the form. 

.. autoclass:: mpeds.classify_protest.MPEDS
   :members: getForm, getFormProb

Issue
-----

The issue variable can take 17 different values: *Abortion, Anti-colonial/political independence, Anti-war/peace, Civic violence, Criminal justice system, Democratization, Economy/inequality, Environmental, Foreign policy, Human and civil rights, Immigration, Labor & work, Political corruption/malfeasance, Racial/ethnic rights, Religion, Social services & welfare*, and *None*.

Classification is made with a linear with a support vector machine (SVM) with a linear kernel. As SVMs do not support class probability estimates, class probabilities are calculated using Platt's method [1]_. For each category, the SVM classifier margins are used to fit a logistic regression model to the training data. These regression models are then used to estimate the probability of a sample belonging to each of the classes. 

.. autoclass:: mpeds.classify_protest.MPEDS
    :members: getIssue, getIssueProb
    
.. [1] Platt, John. "Probabilistic outputs for support vector machines and comparisons to regularized likelihood methods." *Advances in large margin classifiers* 10.3 (1999): 61-74.

Target
------

MPEDS considers seven categories for the target of the protest: *Domestic government, 
Foreign government, Individual, Intergovernmental organization, Private/business, University/school*, and *None*.
       
The target prediction is made with an ensemble classifier consisting of a logistic regression model and a stochastic gradient descent classifier with smoothed hinge loss. The final classification is decided by a soft voting approach.
       
.. autoclass:: mpeds.classify_protest.MPEDS
    :members: getTarget, getTargetProb


Open-ended classifiers
======================

MPEDS extracts information on the protest's size, location, and social movement organizations from the news article. 

Size
----

A pattern matching approach is used to extract the size of any protests mentioned in an article.

.. autoclass:: mpeds.classify_protest.MPEDS
    :members: getSize

Social movement organization
----------------------------

To extract the social movemenent organizations behind a protest, MPEDS uses a custom-trained `Stanford NER classifier <https://nlp.stanford.edu/software/CRF-NER.shtml>`_.

.. autoclass:: mpeds.classify_protest.MPEDS
    :members: getSMO
    
Location
--------

MPEDS uses `CLIFF <http://cliff.mediameter.org>`_ to extract information on the location of the protest. Locations are returned as the most specific geographic entity available (e.g. if a city and a country are mentioned, only the city will be returned).

.. autoclass:: mpeds.classify_protest.MPEDS
    :members: getLocation
    
    