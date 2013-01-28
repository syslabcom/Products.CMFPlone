from persistent.list import PersistentList
from Products.CMFPlone.patches.securemailhost import secureSend
from Products.MailHost.MailHost import _mungeHeaders
from Products.MailHost.MailHost import MailBase
from Testing.ZopeTestCase.functional import ResponseWrapper

import base64
import re
import sys

# regexp for a valid CSS identifier without the leading #
VALID_CSS_ID = re.compile("[A-Za-z_@][A-Za-z0-9_@-]*")


class MockMailHost(MailBase):
    """A MailHost that collects messages instead of sending them.
    """

    def __init__(self, id):
        self.reset()

    def reset(self):
        self.messages = PersistentList()

    def _send(self, mfrom, mto, messageText, immediate=False):
        """ Send the message """
        self.messages.append(messageText)

    def send(self, messageText, mto=None, mfrom=None, subject=None,
             encode=None, immediate=False, charset=None, msg_type=None):
        messageText, mto, mfrom = _mungeHeaders(messageText,
                                                mto, mfrom, subject,
                                                charset=charset,
                                                msg_type=msg_type)
        self.messages.append(messageText)

    # Outside of the tests we patch the MailHost to provide a
    # secureSend method for backwards compatibility, so we should do
    # that for our MockMailHost as well.
    secureSend = secureSend


# a function to test if a string is a valid CSS identifier
def validateCSSIdentifier(identifier):
    match = VALID_CSS_ID.match(identifier)
    if not match is None:
        return match.end() == len(identifier)
    else:
        return False


def publish(REQUEST, path, basic=None, env=None, extra=None,
            request_method='GET', stdin=None, handle_errors=True):
    '''Publishes the object at 'path' returning a response object.'''

    from StringIO import StringIO
    from ZPublisher.Request import Request
    from ZPublisher.Response import Response
    from ZPublisher.Publish import publish_module
    import transaction

    # Commit the sandbox for good measure
    transaction.commit()

    if env is None:
        env = {}
    if extra is None:
        extra = {}

    request = REQUEST

    env['SERVER_NAME'] = request['SERVER_NAME']
    env['SERVER_PORT'] = request['SERVER_PORT']
    env['REQUEST_METHOD'] = request_method

    p = path.split('?')
    if len(p) == 1:
        env['PATH_INFO'] = p[0]
    elif len(p) == 2:
        [env['PATH_INFO'], env['QUERY_STRING']] = p
    else:
        raise TypeError, ''

    if basic:
        env['HTTP_AUTHORIZATION'] = "Basic %s" % base64.encodestring(basic)

    if stdin is None:
        stdin = StringIO()

    outstream = StringIO()
    response = Response(stdout=outstream, stderr=sys.stderr)
    request = Request(stdin, env, response)
    for k, v in extra.items():
        request[k] = v

    publish_module('Zope2',
                   debug=not handle_errors,
                   request=request,
                   response=response,
                  )

    return ResponseWrapper(response, outstream, path)
