from AccessControl import Unauthorized
from OFS.CopySupport import CopyError
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.ATContentTypes.permission import AddTopics
from Products.CMFPlone.tests import dummy
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING

import transaction

#    NOTE
#    document, link, and newsitem edit's are now validated
#    so we must pass in fields that the validators need


class TestContentTypeScripts(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        login(self.portal, TEST_USER_NAME)
        perms = self.getPermissionsOfRole('Member')
        self.setPermissions(
            self.portal.folder, perms + [AddPortalTopics], 'Member')
        self.discussion = self.portal.portal_discussion
        self.request = self.app.REQUEST

    def testDiscussionReply(self):
        from zope.component import createObject, queryUtility
        from plone.registry.interfaces import IRegistry
        from plone.app.discussion.interfaces import IDiscussionSettings
        from plone.app.discussion.interfaces import IConversation
        self.portal.folder.invokeFactory('Document', id='doc', title="Document")
        # Enable discussion
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings)
        settings.globally_enabled = True
        # Create the conversation object
        conversation = IConversation(self.portal.folder.doc)
        # Add a comment
        comment = createObject('plone.Comment')
        comment.text = 'Comment text'
        conversation.addComment(comment)
        # Test the comment
        self.assertEquals(len(list(conversation.getComments())), 1)
        reply = conversation.getComments().next()
        self.assertEqual(reply.Title(), u'Anonymous on Document')
        self.assertEquals(reply.text, 'Comment text')

    def testDocumentCreate(self):
        self.portal.folder.invokeFactory('Document', id='doc', text='data')
        self.assertEqual(self.portal.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.portal.folder.doc.Format(), 'text/plain')

    def testDocumentEdit(self):
        self.portal.folder.invokeFactory('Document', id='doc')
        self.portal.folder.doc.document_edit('html', 'data', title='Foo')
        self.assertEqual(self.portal.folder.doc.EditableBody(), 'data')
        self.assertEqual(self.portal.folder.doc.Format(), 'text/html')
        self.assertEqual(self.portal.folder.doc.Title(), 'Foo')

    def testEventCreate(self):
        self.portal.folder.invokeFactory('Event', id='event',
                                  title='Foo',
                                  start_date='2003-09-18',
                                  end_date='2003-09-19')
        self.assertEqual(self.portal.folder.event.Title(), 'Foo')
        self.assertTrue(self.portal.folder.event.start().ISO8601() \
                            .startswith('2003-09-18T00:00:00'))
        self.assertTrue(self.portal.folder.event.end().ISO8601() \
                            .startswith('2003-09-19T00:00:00'))

    def testEventEdit(self):
        self.portal.folder.invokeFactory('Event', id='event')
        self.portal.folder.event.event_edit(title='Foo',
                                     start_date='2003-09-18',
                                     end_date='2003-09-19')
        self.assertEqual(self.portal.folder.event.Title(), 'Foo')
        self.assertTrue(self.portal.folder.event.start().ISO8601() \
                            .startswith('2003-09-18T00:00:00'))
        self.assertTrue(self.portal.folder.event.end().ISO8601() \
                            .startswith('2003-09-19T00:00:00'))

    def testFileCreate(self):
        self.portal.folder.invokeFactory('File', id='file', file=dummy.File())
        self.assertEqual(str(self.portal.folder.file), dummy.TEXT)

    def testFileEdit(self):
        self.portal.folder.invokeFactory('File', id='file')
        self.portal.folder.file.file_edit(file=dummy.File())
        self.assertEqual(str(self.portal.folder.file), dummy.TEXT)

    def testImageCreate(self):
        self.portal.folder.invokeFactory('Image', id='image', file=dummy.Image())
        self.assertEqual(str(self.portal.folder.image.data), dummy.GIF)

    def testImageEdit(self):
        self.portal.folder.invokeFactory('Image', id='image')
        self.portal.folder.image.image_edit(file=dummy.Image())
        self.assertEqual(str(self.portal.folder.image.data), dummy.GIF)

    def testFolderCreate(self):
        self.portal.folder.invokeFactory('Folder', id='foofolder', title='Foo',
                                  description='Bar')
        self.assertEqual(self.portal.folder.foofolder.Title(), 'Foo')
        self.assertEqual(self.portal.folder.foofolder.Description(), 'Bar')

    def testLinkCreate(self):
        self.portal.folder.invokeFactory('Link', id='link',
                                  remote_url='http://foo.com', title='Foo')
        self.assertEqual(self.portal.folder.link.Title(), 'Foo')
        self.assertEqual(self.portal.folder.link.getRemoteUrl(), 'http://foo.com')

    def testLinkEdit(self):
        self.portal.folder.invokeFactory('Link', id='link')
        self.portal.folder.link.link_edit('http://foo.com', title='Foo')
        self.assertEqual(self.portal.folder.link.Title(), 'Foo')
        self.assertEqual(self.portal.folder.link.getRemoteUrl(), 'http://foo.com')

    def testNewsItemCreate(self):
        self.portal.folder.invokeFactory('News Item', id='newsitem',
                                  text='data', title='Foo')
        self.assertEqual(self.portal.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.portal.folder.newsitem.Title(), 'Foo')

    def testNewsItemEdit(self):
        self.portal.folder.invokeFactory('News Item', id='newsitem')
        self.portal.folder.newsitem.newsitem_edit('data', 'plain', title='Foo')
        self.assertEqual(self.portal.folder.newsitem.EditableBody(), 'data')
        self.assertEqual(self.portal.folder.newsitem.Title(), 'Foo')

    # Bug tests

    def testClearImageTitle(self):
        # Test for http://dev.plone.org/plone/ticket/3303
        # Should be able to clear Image title
        self.portal.folder.invokeFactory('Image', id='image', title='Foo',
                                  file=dummy.Image())
        self.assertEqual(self.portal.folder.image.Title(), 'Foo')
        self.portal.folder.image.image_edit(title='')
        self.assertEqual(self.portal.folder.image.Title(), '')

    def test_listMetaTypes(self):
        self.portal.folder.invokeFactory('Document', id='doc')
        tool = self.portal.plone_utils
        doc = self.portal.folder.doc
        doc.setTitle('title')
        tool.listMetaTags(doc)
        # TODO: atm it checks only of the script can be called w/o an error

    def testObjectDeleteFailsOnGET(self):
        self.assertRaises(Unauthorized, self.portal.folder.object_delete,)

    def testObjectDelete(self):
        self.portal.folder.invokeFactory('Document', id='doc')
        self.setupAuthenticator()
        self.setRequestMethod('POST')
        self.portal.folder.doc.object_delete()
        self.assertFalse('doc' in self.portal.folder)


class TestEditShortName(CMFPloneTestCase):
    # Test fix for http://dev.plone.org/plone/ticket/2246
    # Short name should be editable without specifying a file.

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Owner',])

        self.portal.folder.invokeFactory('File', id='file', file=dummy.File())
        self.portal.folder.invokeFactory('Image', id='image', file=dummy.Image())

    def testFileEditNone(self):
        self.assertEqual(str(self.portal.folder.file), dummy.TEXT)
        self.portal.folder.file.file_edit(file=None, title='Foo')
        self.assertEqual(self.portal.folder.file.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.portal.folder.file), dummy.TEXT)

    def testImageEditNone(self):
        self.assertEqual(str(self.portal.folder.image.data), dummy.GIF)
        self.portal.folder.image.image_edit(file=None, title='Foo')
        self.assertEqual(self.portal.folder.image.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.portal.folder.image.data), dummy.GIF)

    def testFileEditEmptyString(self):
        self.assertEqual(str(self.portal.folder.file), dummy.TEXT)
        self.portal.folder.file.file_edit(file='', title='Foo')
        self.assertEqual(self.portal.folder.file.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.portal.folder.file), dummy.TEXT)

    def testImageEditEmptyString(self):
        self.assertEqual(str(self.portal.folder.image.data), dummy.GIF)
        self.portal.folder.image.image_edit(file='', title='Foo')
        self.assertEqual(self.portal.folder.image.Title(), 'Foo')
        # Data is not changed
        self.assertEqual(str(self.portal.folder.image.data), dummy.GIF)

    def testFileEditString(self):
        self.portal.folder.file.file_edit(file='foo')
        self.assertEqual(str(self.portal.folder.file.getFile()), 'foo')

    def testImageEditString(self):
        self.portal.folder.image.image_edit(file=dummy.GIF)
        self.assertEqual(str(self.portal.folder.image.data), dummy.GIF)

    def testFileEditShortName(self):
        transaction.savepoint(optimistic=True)  # make rename work
        self.portal.folder.file.file_edit(id='fred')
        self.assertTrue('fred' in self.portal.folder)

    def testImageEditShortName(self):
        transaction.savepoint(optimistic=True)  # make rename work
        self.portal.folder.image.image_edit(id='fred')
        self.assertTrue('fred' in self.portal.folder)


class TestEditFileKeepsMimeType(CMFPloneTestCase):
    # Tests covering http://dev.plone.org/plone/ticket/2792
    # Editing a file should not change MIME type

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Owner',])

        self.portal.folder.invokeFactory('File', id='file')
        self.portal.folder.file.file_edit(file=dummy.File('foo.pdf'))
        self.portal.folder.invokeFactory('Image', id='image')
        self.portal.folder.image.image_edit(file=dummy.Image('foo.gif'))

    def testFileMimeType(self):
        self.assertEqual(self.portal.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.portal.folder.file.getFile().content_type,
                         'application/pdf')

    def testImageMimeType(self):
        self.assertEqual(self.portal.folder.image.Format(), 'image/gif')
        self.assertEqual(self.portal.folder.image.content_type, 'image/gif')

    def testFileEditKeepsMimeType(self):
        self.assertEqual(self.portal.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.portal.folder.file.getFile().content_type,
                         'application/pdf')
        self.portal.folder.file.file_edit(title='Foo')
        self.assertEqual(self.portal.folder.file.Title(), 'Foo')
        self.assertEqual(self.portal.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.portal.folder.file.getFile().content_type,
                         'application/pdf')

    def testImageEditKeepsMimeType(self):
        self.assertEqual(self.portal.folder.image.Format(), 'image/gif')
        self.assertEqual(self.portal.folder.image.content_type, 'image/gif')
        self.portal.folder.image.image_edit(title='Foo')
        self.assertEqual(self.portal.folder.image.Title(), 'Foo')
        self.assertEqual(self.portal.folder.image.Format(), 'image/gif')
        self.assertEqual(self.portal.folder.image.content_type, 'image/gif')

    def testFileRenameKeepsMimeType(self):
        self.assertEqual(self.portal.folder.file.Format(), 'application/pdf')
        self.assertEqual(self.portal.folder.file.getFile().content_type,
                         'application/pdf')
        transaction.savepoint(optimistic=True)  # make rename work
        self.portal.folder.file.file_edit(id='foo')
        self.assertEqual(self.portal.folder.foo.Format(), 'application/pdf')
        self.assertEqual(self.portal.folder.foo.getFile().content_type,
                         'application/pdf')

    def testImageRenameKeepsMimeType(self):
        self.assertEqual(self.portal.folder.image.Format(), 'image/gif')
        self.assertEqual(self.portal.folder.image.content_type, 'image/gif')
        transaction.savepoint(optimistic=True)  # make rename work
        self.portal.folder.image.image_edit(id='foo')
        self.assertEqual(self.portal.folder.foo.Format(), 'image/gif')
        self.assertEqual(self.portal.folder.foo.content_type, 'image/gif')


class TestFileURL(CMFPloneTestCase):
    # Tests covering http://dev.plone.org/plone/ticket/3296
    # file:// URLs should contain correct number of slashes
    # NOTABUG: This is how urlparse.urlparse() works.

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def testFileURLWithHost(self):
        self.portal.folder.invokeFactory('Link', id='link',
                                  remote_url='file://foo.com/baz.txt')
        self.assertEqual(self.portal.folder.link.getRemoteUrl(),
                         'file://foo.com/baz.txt')

    def testFileURLNoHost(self):
        self.portal.folder.invokeFactory('Link', id='link',
                                  remote_url='file:///foo.txt')
        self.assertEqual(self.portal.folder.link.getRemoteUrl(), 'file:///foo.txt')

    def testFileURLFourSlash(self):
        self.portal.folder.invokeFactory('Link', id='link',
                                  remote_url='file:////foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.portal.folder.link.getRemoteUrl(),
                         'file://foo.com/baz.txt')

    def testFileURLFiveSlash(self):
        self.portal.folder.invokeFactory('Link', id='link',
                                  remote_url='file://///foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.portal.folder.link.getRemoteUrl(),
                         'file:///foo.com/baz.txt')

    def testFileURLSixSlash(self):
        self.portal.folder.invokeFactory('Link', id='link',
                                  remote_url='file://////foo.com/baz.txt')
        # See urlparse.urlparse()
        self.assertEqual(self.portal.folder.link.getRemoteUrl(),
                         'file:////foo.com/baz.txt')


class TestFileExtensions(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    file_id = 'File.2001-01-01.12345'
    image_id = 'Image.2001-01-01.12345'

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        self.portal.folder.invokeFactory('File', id=self.file_id)
        self.portal.folder.invokeFactory('Image', id=self.image_id)
        transaction.savepoint(optimistic=True)  # make rename work

    def testUploadFile(self):
        self.portal.folder[self.file_id].file_edit(file=dummy.File('fred.txt'))
        self.assertTrue('fred.txt' in self.portal.folder)

    def testUploadImage(self):
        self.portal.folder[self.image_id].image_edit(file=dummy.Image('fred.gif'))
        self.assertTrue('fred.gif' in self.portal.folder)

    def DISABLED_testFileRenameKeepsExtension(self):
        # XXX Wishful thinking
        self.portal.folder[self.file_id].file_edit(id='barney')
        self.assertTrue('barney.txt' in self.portal.folder)

    def DISABLED_testImageRenameKeepsExtension(self):
        # XXX Wishful thinking
        self.portal.folder[self.image_id].image_edit(id='barney')
        self.assertTrue('barney.gif' in self.portal.folder)


class TestBadFileIds(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    file_id = 'File.2001-01-01.12345'
    image_id = 'Image.2001-01-01.12345'

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        self.portal.folder.invokeFactory('File', id=self.file_id)
        self.portal.folder.invokeFactory('Image', id=self.image_id)
        transaction.savepoint(optimistic=True)  # make rename work

    def testUploadBadFile(self):
        # http://dev.plone.org/plone/ticket/3416
        try:
            self.portal.folder[self.file_id].file_edit(file=dummy.File('fred%.txt'))
        except CopyError:
            # Somehow we'd get one of these *sometimes* (not consistently)
            # when running tests... since all we're testing is that the
            # object doesn't get renamed, this shouldn't matter
            pass
        self.assertFalse('fred%.txt' in self.portal.folder)

    def testUploadBadImage(self):
        # http://dev.plone.org/plone/ticket/3518
        try:
            self.portal.folder[self.image_id].image_edit(file=dummy.File('fred%.gif'))
        except CopyError:
            # (ditto - see above)
            pass
        self.assertFalse('fred%.gif' in self.portal.folder)

    # TODO: Dang! No easy way to get at the validator state...


class TestImageProps(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def testImageComputedProps(self):
        from OFS.Image import Image
        tag = Image.tag.im_func
        kw = {'_title': 'some title',
              '_alt': 'alt tag',
              'height': 100,
              'width': 100}
        # Wrap object so that ComputedAttribute gets executed.
        self.ob = dummy.ImageComputedProps(**kw).__of__(self.portal.folder)

        endswith = ('alt="alt tag" title="some title" '
                    'height="100" width="100" />')
        self.assertEqual(tag(self.ob)[-len(endswith):], endswith)
