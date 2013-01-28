from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from Products.ATContentTypes.interfaces import IATContentType
from Products.ATContentTypes.permission import AddTopics
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING
from zope.i18nmessageid.message import Message

atct_types = ('Document', 'Event', 'File', 'Folder',
              'Image', 'Link', 'News Item',
             )


class TestATContentTypes(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        perms = self.getPermissionsOfRole('Member')
        self.types = self.portal.portal_types

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def construct(self, portal_type, id, folder):
        fti = self.types.getTypeInfo(portal_type)
        fti.constructInstance(folder, id=id)
        return getattr(folder, id)

    def createWithoutConstruction(self, portal_type, id, folder):
        fti = self.types.getTypeInfo(portal_type)
        # manual creation
        p = folder.manage_addProduct[fti.product]
        m = getattr(p, fti.factory)
        m(id)  # create it
        return folder._getOb(id)

    def testPortalTypeName(self):
        for pt in atct_types:
            ob = self.construct(pt, pt, self.portal.folder)
            self.assertEqual(ob._getPortalTypeName(), pt)
            self.assertEqual(ob.portal_type, pt)
            self.assertTrue(IATContentType.providedBy(ob))


class TestContentTypes(CMFPloneTestCase):
    # This test mirrors TestContentTypeScripts but calls the API and
    # not the skin scripts.

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(self.portal.folder, perms + [AddTopics], 'Member')

    def getPermissionsOfRole(self, role):
        perms = self.portal.permissionsOfRole(role)
        return [p['name'] for p in perms if p['selected']]

    def testDocumentEdit(self):
        self.portal.folder.invokeFactory('Document', id='doc')
        self.portal.folder.doc.edit(title='Foo', text='data', text_format='html')
        self.assertEqual(self.portal.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.portal.folder.doc.Format(), 'text/html')
        self.assertEqual(self.portal.folder.doc.Title(), 'Foo')

    def testEventEdit(self):
        self.portal.folder.invokeFactory('Event', id='event')
        self.portal.folder.event.edit(title='Foo',
                               start_date='2003-09-18',
                               end_date='2003-09-19')
        self.assertEqual(self.portal.folder.event.Title(), 'Foo')
        self.assertTrue(self.portal.folder.event.start().ISO8601() \
                            .startswith('2003-09-18T00:00:00'))
        self.assertTrue(self.portal.folder.event.end().ISO8601() \
                            .startswith('2003-09-19T00:00:00'))

    def testFileEdit(self):
        self.portal.folder.invokeFactory('File', id='file')
        self.portal.folder.file.edit(file=dummy.File())
        self.assertEqual(str(self.portal.folder.file), dummy.TEXT)

    def testImageEdit(self):
        self.portal.folder.invokeFactory('Image', id='image')
        self.portal.folder.image.edit(file=dummy.Image())
        self.assertEqual(str(self.portal.folder.image.data), dummy.GIF)

    def testFolderEdit(self):
        self.portal.folder.invokeFactory('Folder', id='folder')
        self.portal.folder.edit(title='Foo', description='Bar')
        self.assertEqual(self.portal.folder.Title(), 'Foo')
        self.assertEqual(self.portal.folder.Description(), 'Bar')
        # Edit a second time
        self.portal.folder.edit(title='Fred', description='BamBam')
        self.assertEqual(self.portal.folder.Title(), 'Fred')
        self.assertEqual(self.portal.folder.Description(), 'BamBam')

    def testLinkEdit(self):
        self.portal.folder.invokeFactory('Link', id='link')
        self.portal.folder.link.edit(remote_url='http://foo.com', title='Foo')
        self.assertEqual(self.portal.folder.link.Title(), 'Foo')
        self.assertEqual(self.portal.folder.link.getRemoteUrl(), 'http://foo.com')

    def testNewsItemEdit(self):
        self.portal.folder.invokeFactory('News Item', id='newsitem')
        self.portal.folder.newsitem.edit(text='data', text_format='html', title='Foo')
        self.assertEqual(self.portal.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.portal.folder.newsitem.Format(), 'text/html')
        self.assertEqual(self.portal.folder.newsitem.Title(), 'Foo')

    def testTopicEdit(self):
        self.portal.portal_types.Topic.global_allow = True
        self.portal.folder.invokeFactory('Topic', id='topic')
        self.portal.folder.topic.edit(title='Foo')
        self.assertEqual(self.portal.folder.topic.Title(), 'Foo')


class TestContentTypeInformation(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        self.types = self.portal.portal_types

    def testTypeTitlesAreMessages(self):
        for t in self.types.values():
            # If the title is empty we get back the id
            if t.title:
                self.assertTrue(isinstance(t.Title(), Message))
            # Descriptions may be blank. Only check if there's a value.
            if t.description:
                self.assertTrue(isinstance(t.Description(), Message))
