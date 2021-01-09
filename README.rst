cyberspacy: cybersecurity datatypes for spaCy
*********************************************

`spaCy v2.0 <https://spacy.io/usage/v2>`_ extension and pipeline component
for adding meta data about IPs, email addresses and URLs to ``Doc`` objects.
Heavily inspired by `spacymoji <https://github.com/ines/spacymoji>`_.

Installation
===============

``cyberspacy`` requires ``spacy`` v2.0.0 or higher.

pip
---

.. code:: bash

    pip install cyberspacy

Usage
========

Import the component and initialise it with the shared ``nlp`` object (i.e. an
instance of ``Language``), which is used to initialise the ``PhraseMatcher``
with the shared vocab, and create the match patterns. Then add the component
anywhere in your pipeline.

.. code:: python

    import spacy
    from spacy.lang.en import English
    from cyberspacy import IPTagger
    nlp = English()
    ip_Tagger = IPTagger(nlp)
    nlp.add_pipe(ip_Tagger, first=True)
    doc = nlp(u'This is a sentence which contains 2.3.4.5 as an IP address')
    assert doc._.has_ipv4 == True
    assert doc[0]._.is_ipv4 == False
    assert doc[6]._.is_ipv4 == True
    assert len(doc._.ipv4) == 1
    idx, ipv4_token = doc._.ipv4[0]
    assert idx == 6
    assert ipv4_token.text == '2.3.4.5'

``cyberspacy`` only cares about the token text, so you can use it on a blank
``Language`` instance (it should work for all
`available languages <https://spacy.io/usage/models#languages>`_!), or in
a pipeline with a loaded model. 

Available attributes
--------------------

The extension sets attributes on the ``Doc``, ``Span`` and ``Token``. You can
change the attribute names on initialisation of the extension. For more details
on custom components and attributes, see the
`processing pipelines documentation <https://spacy.io/usage/processing-pipelines#custom-components>`_.

The attributes provided by the IPTagger class are:

===================== ======= ===
``Token._.is_ipv4``   bool    Whether the token is an IPv4 address.
``Doc._.has_ipv4``    bool    Whether the document contains an IPv4 address.
``Doc._.ipv4``        list    ``(index, token)`` tuples of the document's IPv4 addresses.
``Span._.has_ipv4``   bool    Whether the span contains IPv4 addresses.
``Span._.ipv4``       list    ``(index, token)`` tuples of the span's IPv4 addresses.
===================== ======= ===

The attributes provided by the URLTagger class are:

==================== ======= ===
``Token._.is_url``   bool    Whether the token is a URL.
``Doc._.has_url``    bool    Whether the document contains a URL.
``Doc._.url``        list    ``(index, token)`` tuples of the document's URLs.
``Span._.has_url``   bool    Whether the span contains a URL.
``Span._.url``       list    ``(index, token)`` tuples of the span's URLs.
==================== ======= ===

The attributes provided by the EmailTagger class are:

=========================   ======= ===
``Token._.is_email_addr``   bool    Whether the token is an email address.
``Doc._.has_email_addr``    bool    Whether the document contains an email address.
``Doc._.email_addr``        list    ``(index, token)`` tuples of the document's email addresses.
``Span._.has_email_addr``   bool    Whether the span contains an email address.
``Span._.email_addr``       list    ``(index, token)`` tuples of the span's email addresses.
=========================   ======= ===



