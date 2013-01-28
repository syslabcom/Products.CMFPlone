# Example PloneTestCase

from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING

from Acquisition import aq_base


class TestPloneTestCase(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow
        self.setupAuthenticator()

    def testAddDocument(self):
        self.assertFalse(self.catalog(id='new'))
        self.folder.invokeFactory('Document', id='new')
        self.assertTrue(hasattr(aq_base(self.folder), 'new'))
        self.assertTrue(self.catalog(id='new'))

    def testPublishDocument(self):
        self.folder.invokeFactory('Document', id='new')
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        self.workflow.doActionFor(self.folder.new, 'publish')
        self.assertEqual(
                self.workflow.getInfoFor(self.folder.new, 'review_state'),
                'published')
        self.assertTrue(self.catalog(id='new', review_state='published'))

    def testRetractDocument(self):
        self.folder.invokeFactory('Document', id='new')
        setRoles(self.portal, TEST_USER_ID, ['Reviewer'])
        self.workflow.doActionFor(self.folder.new, 'publish')
        self.assertEqual(
                self.workflow.getInfoFor(self.folder.new, 'review_state'),
                'published')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.workflow.doActionFor(self.folder.new, 'retract')
        self.assertEqual(
                self.workflow.getInfoFor(self.folder.new, 'review_state'),
                'visible')

    def testEditDocument(self):
        self.folder.invokeFactory('Document', id='new')
        self.assertEqual(self.folder.new.EditableBody(), '')
        self.folder.new.edit('plain', 'data', file='', safety_belt='')
        self.assertEqual(self.folder.new.EditableBody(), 'data')

    def testGetterSkinScript(self):
        self.folder.invokeFactory('Document', id='new', title='Foo')
        self.assertEqual(self.folder.new.TitleOrId(), 'Foo')

    def testSetterSkinScript(self):
        self.folder.invokeFactory('Document', id='new')
        self.assertEqual(self.folder.new.EditableBody(), '')
        self.folder.new.document_edit('plain', 'data', title='Foo')
        self.assertEqual(self.folder.new.EditableBody(), 'data')
