from AccessControl import Unauthorized
from Acquisition import aq_base
from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING

import unittest


class TestContentSecurity(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        setRoles(self.portal, TEST_USER_ID, ['Manager',])
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.portal.acl_users._doAddUser('user2', 'secret', ['Member'], [])
        #_ender_'s member who's not a Member usecase
        self.portal.acl_users._doAddUser('user3', 'secret', [], [])
        self.membership = self.portal.portal_membership
        # allow memberareaCreationFlag for users who don't self-register
        self.membership.memberareaCreationFlag = True
        self.workflow = self.portal.portal_workflow
        self.membership.createMemberArea('user1')
        self.membership.createMemberArea('user2')
        logout()

    def testCreateMemberContent(self):
        login(self.portal, 'user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')
        self.assertTrue(hasattr(aq_base(folder), 'new'))

    def testCreateOtherMemberContentFails(self):
        login(self.portal, 'user1')
        folder = self.membership.getHomeFolder('user2')
        self.assertRaises(ValueError, folder.invokeFactory, 'Document', 'new')

    def testCreateRootContentFails(self):
        login(self.portal, 'user1')
        self.assertRaises(Unauthorized, self.portal.invokeFactory,
                          'Document', 'new')

    def testDeleteMemberContent(self):
        login(self.portal, 'user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')
        folder.manage_delObjects(['new'])
        self.assertFalse(hasattr(aq_base(folder), 'new'))

    def testDeleteOtherMemberContent(self):
        login(self.portal, 'user1')
        folder = self.membership.getHomeFolder('user1')
        folder.invokeFactory('Document', id='new')

        login(self.portal, 'user2')
        folder = self.membership.getHomeFolder('user1')
        self.assertRaises(Unauthorized, folder.manage_delObjects, ['new'])

    def testCreateWithLocalRole(self):
        login(self.portal, 'user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Owner',))
        login(self.portal, 'user2')
        # This will raise Unauthorized if the role is not set
        folder.invokeFactory('Document', id='new')

    def testCreateFailsWithLocalRoleBlocked(self):
        # Ensure that local role blocking works for blocking content creation
        login(self.portal, 'user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Owner',))

        sharingView = self.portal.folder.unrestrictedTraverse('@@sharing')
        sharingView.update_role_settings([{'id':'user2',
                                           'type':'user',
                                           'roles':['Owner']}])

        folder.invokeFactory('Folder', id='subfolder')
        #Turn off local role acquisition
        folder.subfolder.unrestrictedTraverse('@@sharing') \
                .update_inherit(False)

        login(self.portal, 'user2')
        # This should now raise ValueError
        self.assertRaises(ValueError, folder.subfolder.invokeFactory,
                          'Document', 'new')

    def testCreateSucceedsWithLocalRoleBlockedInParentButAssingedInSubFolder(self):
        # Make sure that blocking a acquisition in a folder does not interfere
        # with assigning a role in subfolders
        login(self.portal, 'user1')
        folder = self.membership.getHomeFolder('user1')
        folder.manage_addLocalRoles('user2', ('Owner',))
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        #Turn off local role acquisition
        subfolder.unrestrictedTraverse('@@sharing').update_inherit(False)
        subfolder.invokeFactory('Folder', id='subsubfolder')
        subfolder.subsubfolder.manage_addLocalRoles('user2', ('Owner',))
        login(self.portal, 'user2')
        # This should not raise Unauthorized
        subfolder.subsubfolder.invokeFactory('Document', id='new')

    def testViewAllowedOnContentInAcquisitionBlockedFolder(self):
        # Test for http://dev.plone.org/plone/ticket/4055 which seems to be
        # invalid
        login(self.portal, 'user1')
        self.setupAuthenticator()
        folder = self.membership.getHomeFolder('user1')
        self.setRequestMethod('POST')
        folder.manage_addLocalRoles('user2', ('Owner',))
        self.setRequestMethod('GET')
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        subfolder.unrestrictedTraverse('@@sharing').update_inherit(False)
        #Turn off local role acquisition
        subfolder.invokeFactory('Document', id='new')
        subfolder.new.content_status_modify(workflow_action='publish')
        subfolder.new.manage_addLocalRoles('user2', ('Member',))
        login(self.portal, 'user2')
        # This should not raise Unauthorized
        subfolder.new.base_view()

    def testViewAllowedOnContentInPrivateFolder(self):
        login(self.portal, 'user1')
        folder = self.membership.getHomeFolder('user1')
        folder.content_status_modify(workflow_action='private')
        folder.invokeFactory('Document', id='doc1')
        doc = folder.doc1
        doc.content_status_modify(workflow_action='publish')
        doc.manage_addLocalRoles('user2', ('Owner',))
        login(self.portal, 'user2')
        self.request['ACTUAL_URL'] = doc.absolute_url()
        # This should not raise Unauthorized
        doc.base_view()
        # Neither should anonymous
        logout()
        doc.base_view()

    def testViewAllowedOnContentInAcquisitionBlockedFolderWithCustomWorkflow(self):
        # Another test for http://dev.plone.org/plone/ticket/4055
        # using a paired down version of the custom workflow described therein
        # 'Access contents information' must be enabled for Authenticated/
        # Anonymous on folders for even simple actions to evaluate properly.

        # Create more private workflow starting with folder_workflow
        wf = self.portal.portal_workflow.folder_workflow
        visible = wf.states.visible
        visible.setPermission('View', 0, ('Manager', 'Owner'))
        visible.setPermission('Modify portal content', 0, ('Manager', 'Owner'))
        # Then plone workflow
        p_wf = self.portal.portal_workflow.plone_workflow
        published = p_wf.states.published
        published.setPermission('View', 0, ('Manager', 'Member', 'Owner'))
        published.setPermission('Access contents information', 0,
                                ('Manager', 'Member', 'Owner'))
        published.setPermission('Modify portal content', 0,
                                ('Manager', 'Member', 'Owner'))
        self.portal.portal_workflow.updateRoleMappings()

        login(self.portal, 'user1')
        self.setupAuthenticator()
        self.setRequestMethod('POST')
        folder = self.membership.getHomeFolder('user1')
        self.setRequestMethod('GET')
        folder.manage_addLocalRoles('user2', ('Member',))
        folder.invokeFactory('Folder', id='subfolder')
        subfolder = folder.subfolder
        subfolder.unrestrictedTraverse('@@sharing').update_inherit(False)
        subfolder.invokeFactory('Document', id='new')
        subfolder.new.content_status_modify(workflow_action='publish')
        subfolder.new.manage_addLocalRoles('user3', ('Member',))
        login(self.portal, 'user3')
        # This shouldn't either, but strangely it never does even if the script
        # below, which is called in here, does.  What is wrong here?
        try:
            subfolder.new.base_view()
        except Unauthorized:
            self.fail("Could not access base_view on 'new'")
        # This should not raise Unauthorized
