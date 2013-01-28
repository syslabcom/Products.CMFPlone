from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.factory import _DEFAULT_PROFILE
from Products.CMFPlone.tests.CMFPloneTestCase import CMFPloneTestCase
from Products.CMFPlone.tests.layers import PLONE_TEST_CASE_INTEGRATION_TESTING


class TestMigrationTool(CMFPloneTestCase):

    layer = PLONE_TEST_CASE_INTEGRATION_TESTING

    def setUp(self):
        CMFPloneTestCase.setUp(self)
        self.migration = getToolByName(self.portal, "portal_migration")
        self.setup = getToolByName(self.portal, "portal_setup")

    def testMigrationFinished(self):
        self.assertEqual(self.migration.getInstanceVersion(),
                         self.migration.getFileSystemVersion(),
                         'Migration failed')

    def testMigrationNeedsUpgrading(self):
        self.assertFalse(self.migration.needUpgrading(),
                    'Migration needs upgrading')

    def testMigrationNeedsUpdateRole(self):
        self.assertFalse(self.migration.needUpdateRole(),
                    'Migration needs role update')

    def testMigrationNeedsRecatalog(self):
        self.assertFalse(self.migration.needRecatalog(),
                    'Migration needs recataloging')

    def testListUpgradeSteps(self):
        # There should be no upgrade steps from the current version
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertTrue(len(upgrades) == 0)

    def testDoUpgrades(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.setup.setLastVersionForProfile(_DEFAULT_PROFILE, '2.5')
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertTrue(len(upgrades) > 0)

        request = self.portal.REQUEST
        request.form['profile_id'] = _DEFAULT_PROFILE

        steps = []
        for u in upgrades:
            if isinstance(u, list):
                steps.extend([s['id'] for s in u])
            else:
                steps.append(u['id'])

        request.form['upgrades'] = steps
        self.setup.manage_doUpgrades(request=request)

        # And we have reached our current profile version
        current = self.setup.getVersionForProfile(_DEFAULT_PROFILE)
        current = tuple(current.split('.'))
        last = self.setup.getLastVersionForProfile(_DEFAULT_PROFILE)
        self.assertEquals(last, current)

        # There are no more upgrade steps available
        upgrades = self.setup.listUpgrades(_DEFAULT_PROFILE)
        self.assertTrue(len(upgrades) == 0)
