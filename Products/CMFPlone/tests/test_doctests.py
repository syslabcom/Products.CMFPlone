from doctest import DocFileSuite
from doctest import DocTestSuite
from plone.testing import layered
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_FUNCTIONAL_TESTING
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING
import doctest
import unittest

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([

        layered(DocFileSuite('mails.rst',
                             package = 'Products.CMFPlone.tests',
                             optionflags = OPTIONFLAGS),
                layer = PLONE_TEST_CASE_INTEGRATION_TESTING),

        layered(DocFileSuite('emaillogin.rst',
                             package = 'Products.CMFPlone.tests',
                             optionflags = OPTIONFLAGS),
                layer = PLONE_TEST_CASE_INTEGRATION_TESTING),

        layered(DocTestSuite('Products.CMFPlone.CatalogTool',
                             optionflags = OPTIONFLAGS),
                layer = PLONE_TEST_CASE_FUNCTIONAL_TESTING),

        layered(DocTestSuite('Products.CMFPlone.PloneTool',
                             optionflags = OPTIONFLAGS),
                layer = PLONE_TEST_CASE_FUNCTIONAL_TESTING),

        DocFileSuite('messages.rst',
                     package='Products.CMFPlone.tests'),
        DocTestSuite('Products.CMFPlone.CalendarTool'),
        DocTestSuite('Products.CMFPlone.i18nl10n'),
        DocTestSuite('Products.CMFPlone.TranslationServiceTool'),
        DocTestSuite('Products.CMFPlone.utils'),
        DocTestSuite('Products.CMFPlone.workflow'),

    ])
    return suite
