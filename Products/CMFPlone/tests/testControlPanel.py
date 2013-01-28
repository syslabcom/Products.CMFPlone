from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_FUNCTIONAL_TESTING

class TestControlPanel(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_FUNCTIONAL_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        self.controlpanel = getToolByName(self.portal, "portal_controlpanel")

        # get the expected default groups and configlets
        self.groups = ['Plone', 'Products']
        self.configlets = ['QuickInstaller', 'portal_atct', 'MailHost',
                           'UsersGroups', 'MemberPrefs', 'PortalSkin',
                           'MemberPassword', 'ZMI', 'SecuritySettings',
                           'NavigationSettings', 'SearchSettings',
                           'errorLog', 'PloneReconfig',
                           'CalendarSettings', 'TypesSettings',
                           'PloneLanguageTool', 'CalendarSettings',
                           'HtmlFilter', 'Maintenance']

    def testDefaultGroups(self):
        for group in self.groups:
            self.assertTrue(group in self.controlpanel.getGroupIds(),
                            "Missing group with id '%s'" % group)

    def testDefaultConfiglets(self):
        for title in self.configlets:
            self.assertTrue(title in [a.getAction(self)['id']
                                   for a in self.controlpanel.listActions()],
                            "Missing configlet with id '%s'" % title)
