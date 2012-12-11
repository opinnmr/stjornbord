from django.views.decorators.cache import never_cache
from django.shortcuts import render_to_response
from django.contrib.auth.forms import AuthenticationForm
from django.template.context import RequestContext
from django.contrib.auth import login as auth_login
from django.conf import settings

import logging
from samlResponse import SAML2Response
from datetime import datetime

privateKeyFileName = settings.SAML2IDP_PRIVATE_KEY_FILE
certificateFileName = settings.SAML2IDP_CERTIFICATE_FILE

samlResp = SAML2Response(privateKeyFileName, certificateFileName)

auth_log = logging.getLogger("stjornbord.saml")

@never_cache
def assertView(request, template_name='registration/login.html'):
    """
    If user is authenticated simple returns SAML response.
    Else displays login screen and tries to authenticate user.
    The SAML response is sent upon successful authentication.
    """     
    # Always ask for username/password when authenticating
    #   2011-08-07 <bjorn swift>
    #
    #if request.user.is_authenticated():
    #    return _sso_post_response(request)
    
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())

            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()

            auth_log.info("SAML authentication success, user=%s", request.POST["username"].encode("utf8"))

            return _sso_post_response(request)
        else:
            auth_log.warning("SAML authentication failure, user=%s", request.POST["username"].encode("utf8"))
    else:
        form = AuthenticationForm(request)
    
    return render_to_response(template_name, {
        'form': form,
        'webmail': True,
    }, context_instance=RequestContext(request))


def _sso_post_response(request):
    """
    Returns an HTML form that will POST back to the Service Point.
    """
    samlResponse, respURL = samlResp.getLoginResponse(request)
    
    token = request.GET.get('RelayState', None)
    return render_to_response('saml2idp/sso_post_response.html', {
        'response_url': respURL,
        'saml_response': samlResponse,
        'token': token,
    }, context_instance=RequestContext(request))

#@never_cache
#def assertView(request, loginUrl=settings.LOGIN_URL, ssoUrl=settings.SSO_URL):
#    """
#    If user is not yet logged, redirect to login page.
#    Else return SAML response to IDC.
#    """
#    if request.user.is_authenticated():
#        return _sso_post_response(request)
#    else:
#        getParams = ['%s=%s' % (k, v) for k, v in request.GET.items()]
#        return HttpResponseRedirect('%s?next=%s&%s' % 
#                                    (loginUrl, ssoUrl, '&'.join(getParams)))