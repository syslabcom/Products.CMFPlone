# This test confirms that views assigned to theme-specific layers (a la
# plone.theme) take precedence over views assigned to layers from other
# add-on products (a la plone.browserlayer).

from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.browserlayer.utils import register_layer, unregister_layer
from plonetheme.sunburst.browser.interfaces import IThemeSpecific
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_FUNCTIONAL_TESTING
from zope.event import notify
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.traversing.interfaces import BeforeTraverseEvent


class IAdditiveLayer(Interface):
    pass


class TestBrowserLayerPrecedence(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_FUNCTIONAL_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ['Owner'])

    def _get_request_interfaces(self):
        request = TestRequest()
        notify(BeforeTraverseEvent(self.portal, request))
        iro = list(request.__provides__.__iro__)
        return iro

    def testCustomBrowserLayerHasPrecedenceOverDefaultLayer(self):
        register_layer(IAdditiveLayer, 'Plone.testlayer')
        iro = self._get_request_interfaces()
        unregister_layer('Plone.testlayer')

        self.assertTrue(iro.index(IAdditiveLayer) < iro.index(IDefaultBrowserLayer))

    def testThemeSpecificLayerTakesHighestPrecedence(self):
        register_layer(IAdditiveLayer, 'Plone.testlayer')
        iro = self._get_request_interfaces()
        unregister_layer('Plone.testlayer')

        self.assertTrue(iro.index(IThemeSpecific) < iro.index(IAdditiveLayer),
            'Theme-specific browser layers should take precedence over other '
            'browser layers.')
