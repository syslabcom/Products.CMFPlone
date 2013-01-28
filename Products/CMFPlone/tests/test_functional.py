from plone.testing import layered
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_FUNCTIONAL_TESTING

import doctest
import glob
import os
import unittest

UNITTESTS = ['messages.rst', 'mails.rst', 'emaillogin.rst']
OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def list_doctests():
    filenames = glob.glob(
        os.path.sep.join([os.path.dirname(__file__), '*.rst']))
    return [os.path.basename(filename)
            for filename in filenames
            if os.path.basename(filename) not in UNITTESTS]

def test_suite():
    filenames = list_doctests()
    suite = unittest.TestSuite()
    for filename in filenames:
        suite.addTests([
            layered(doctest.DocFileSuite(filename,
                                         package = 'Products.CMFPlone.tests',
                                         optionflags = OPTIONFLAGS),
                    layer = PLONE_TEST_CASE_FUNCTIONAL_TESTING)
        ])
    return suite
