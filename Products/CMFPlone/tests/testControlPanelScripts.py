from cStringIO import StringIO
from DateTime import DateTime
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneFunctionalTestCase
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_FUNCTIONAL_TESTING
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING
from zExceptions import Forbidden


class TestNoGETControlPanel(CMFPloneFunctionalTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneFunctionalTestCase.setUp(self)
        self.folder_path = '/' + self.portal.folder.absolute_url(1)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.portal_membership.addMember('bribri', 'secret',
                                                ['Manager'], [])
        login(self.portal, 'bribri')

    def _onlyPOST(self, path, qstring='', success=200, rpath=None):
        qstring += '&%s=%s' % self.getAuthenticator()
        basic_auth = '%s:%s' % ('bribri', 'secret')
        env = dict()
        if rpath:
            env['HTTP_REFERER'] = self.app.absolute_url() + rpath
        response = self.publish('%s?%s' % (path, qstring), basic_auth, env,
                                handle_errors=True)
        self.assertEqual(response.getStatus(), 403)

        data = StringIO(qstring)
        if 'QUERY_STRING' in env:
            del env['QUERY_STRING']
        response = self.publish(path, basic_auth, env, request_method='POST',
                                stdin=data)
        self.assertEqual(response.getStatus(), success)

    def test_changeOwnership(self):
        path = self.folder_path + '/change_ownership'
        qstring = 'userid=%s' % TEST_USER_NAME
        self._onlyPOST(path, qstring, success=302)

    def test_loginChangePassword(self):
        path = self.folder_path + '/login_change_password'
        qstring = 'password=foo'
        self._onlyPOST(path, qstring)


class TestPrefsUserManage(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        self.membership = self.portal.portal_membership
        self.membership.memberareaCreationFlag = 0
        self.setupAuthenticator()

    def addMember(self, username, fullname, email, roles, last_login_time):
        self.membership.addMember(username, 'secret', roles, [])
        member = self.membership.getMemberById(username)
        member.setMemberProperties({
                        'fullname': fullname,
                        'email': email,
                        'last_login_time': DateTime(last_login_time), })

    def test_ploneChangePasswordPostOnly(self):
        login(self.portal, TEST_USER_NAME)
        self.setRequestMethod('GET')
        self.assertRaises(Forbidden, self.portal.plone_change_password,
                          current=TEST_USER_PASSWORD, password=TEST_USER_PASSWORD,
                          password_confirm=TEST_USER_PASSWORD)


class TestAccessControlPanelScripts(CMFPloneFunctionalTestCase):
    '''Yipee, functional tests'''

    layer = PLONE_TEST_CASE_FUNCTIONAL_TESTING

    def setUp(self):
        CMFPloneFunctionalTestCase.setUp(self)
        self.portal_path = self.portal.absolute_url(1)
        self.basic_auth = '%s:%s' % (TEST_USER_NAME, TEST_USER_PASSWORD)

    def testUserInformation(self):
        '''Test access to user details.'''
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        # import pdb;pdb.set_trace()
        response = self.publish('%s/@@user-information?userid=%s' %
                                (self.portal_path, TEST_USER_ID),
                                self.basic_auth)

        self.assertEquals(response.getStatus(), 200)

    def testUserPreferences(self):
        '''Test access to user details.'''
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        response = self.publish('%s/@@user-preferences?userid=%s' %
                                (self.portal_path, TEST_USER_ID),
                                self.basic_auth)

        self.assertEquals(response.getStatus(), 200)
