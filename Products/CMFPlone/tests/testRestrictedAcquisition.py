#
# This test module demonstrates a problem caused by the removal of
# a few lines of code from cAccessControl.c and ImplPython.c
# See: http://mail.zope.org/pipermail/zope-checkins/2004-August/028152.html
#
# If an object with setDefaultAccess('deny') is used as the context for
# a PythonScript, the script can no longer aquire tools from the portal
# root. Rolling back the abovementioned checkin restores functionality.
#

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING


class AllowedItem(SimpleItem):
    id = 'allowed'
    security = ClassSecurityInfo()
    security.setDefaultAccess('allow')

InitializeClass(AllowedItem)

class DeniedItem(SimpleItem):
    id = 'denied'
    security = ClassSecurityInfo()
    security.setDefaultAccess('deny')

InitializeClass(DeniedItem)


class BrokenAcquisitionTest(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        self.portal.folder._setObject('allowed', AllowedItem())
        self.portal.folder._setObject('denied', DeniedItem())

    def _makePS(self, context, id, params, body):
        factory = context.manage_addProduct['PythonScripts']
        factory.manage_addPythonScript(id)
        ps = context[id]
        ps.ZPythonScript_edit(params, body)

    def testAcquisitionAllowed(self):
        self._makePS(self.portal.folder, 'ps', '', 'print context.portal_membership')
        self.portal.folder.allowed.ps()

    def testAcquisitionDenied(self):
        # This test fails in Zope 2.7.3
        # Also see http://zope.org/Collectors/CMF/259
        self._makePS(self.portal.folder, 'ps', '', 'print context.portal_membership')
        self.portal.folder.denied.ps()
