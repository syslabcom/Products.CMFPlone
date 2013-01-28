# -*- coding: utf-8 -*-

from Products.CMFPlone.factory import addPloneSite
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING


class TestFactoryPloneSite(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def testPlonesiteWithUnicodeTitle(self):
        TITLE = 'Ploné'
        ploneSite = addPloneSite(self.app, 'ploneFoo', title=TITLE,
                     setup_content=False)
        ploneSiteTitleProperty = ploneSite.getProperty('title')
        # CMF stores title as string only so Plone should keep the same track
        self.assertTrue(isinstance(ploneSiteTitleProperty, str))
        self.assertEqual(ploneSiteTitleProperty, TITLE)
        ploneSiteTitle = ploneSite.Title()
        self.assertTrue(isinstance(ploneSiteTitle, str))
        self.assertEqual(ploneSiteTitle, TITLE)

    def testPlonesiteWithoutUnicodeTitle(self):
        TITLE = 'Plone'
        ploneSite = addPloneSite(self.app, 'ploneFoo', title=TITLE,
                     setup_content=False)
        ploneSiteTitleProperty = ploneSite.getProperty('title')
        # CMF stores title as string only so Plone should keep the same track
        self.assertTrue(isinstance(ploneSiteTitleProperty, str))
        self.assertEqual(ploneSiteTitleProperty, TITLE)
        ploneSiteTitle = ploneSite.Title()
        self.assertTrue(isinstance(ploneSiteTitle, str))
        self.assertEqual(ploneSiteTitle, TITLE)
