#
# Test methods used to make browser-default-mixin enabled display menu work
#

from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING


class TestBrowserDefaultScripts(CMFPloneTestCase):
    """Tests the browser default and folder-default page scripts"""

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def testNoIndexHtml(self):
        # A folder shouldn't have an index_html object at instantiation time
        self.assertFalse(self.portal.folder.hasIndexHtml())

    def testHasIndexHtml(self):
        # Make sure we can determine if a container contains a index_html
        # object
        self.portal.folder.invokeFactory('Document', 'index_html',
                                  title='Test index')
        self.assertTrue(self.portal.folder.hasIndexHtml())

    def testGetSelectableViewsWithViews(self):
        # Assume folders have at least two possible views to chose from
        views = [v[0] for v in self.portal.folder.getSelectableViews()]
        self.assertTrue(views)
        self.assertTrue('folder_listing' in views)
        self.assertTrue('atct_album_view' in views)

    def testGetSelectableViewsWithoutViews(self):
        # Assume documents have only one view
        self.portal.folder.invokeFactory('Document', 'test',
                                  title='Test default page')
        doc = getattr(self.portal.folder, 'test')
        self.assertFalse(doc.getSelectableViews())

    def testSetDefaultPageWithoutPage(self):
        # Make sure we can't define a default page if no object in folder
        self.assertTrue(self.portal.folder.canSelectDefaultPage())
