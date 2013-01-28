from DateTime import DateTime
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING


class TestDateIndexRanges(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase(self)
        self.catalog = self.portal.portal_catalog
        self.folder.invokeFactory('Document', 'doc1', title='Foo')

    def testHiWatermark(self):
        self.folder.doc1.setExpirationDate(DateTime(4008, 0))
        self.folder.doc1.reindexObject()

    def testOverflow(self):
        self.folder.doc1.setExpirationDate(DateTime(4009, 0))
        # No OverflowError due to monkey patch
        #self.assertRaises(OverflowError, self.folder.doc1.reindexObject)
        self.folder.doc1.reindexObject()

    def testDRIOverflow(self):
        self.folder.doc1.setEffectiveDate(DateTime(4009, 0))
        # No OverflowError due to monkey patch
        #self.assertRaises(OverflowError, self.folder.doc1.reindexObject)
        self.folder.doc1.reindexObject()
