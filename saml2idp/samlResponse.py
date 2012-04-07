
import time    
import zlib
import base64
from xml.dom.minidom import parseString

from saml2.saml import AuthnStatement, Subject, SubjectConfirmation,\
    SubjectConfirmationData, Conditions, Audience, AudienceRestriction,\
    AuthnContext, AuthnContextClassRef, Assertion, NameID, Issuer
from saml2.samlp import Response, Status, StatusCode
from saml2.utils import createID, sign
from xmldsig import Signature, SignedInfo, Reference, DigestValue, DigestMethod,\
    Transform, Transforms, SignatureMethod, CanonicalizationMethod,\
    SignatureValue


class SAML2Response:
    """
    Class for SAML 2.0 response construction.
    Tested with Google Apps.
    See sample response at:
    http://code.google.com/p/google-apps-sso-sample/source/browse/trunk/php/SAMLTestTool/templates/SamlResponseTemplate.xml
    """
    
    def __init__(self, privateKeyFileName, certificateFileName):
        self.privateKeyFileName = privateKeyFileName
        self.certificateFileName = certificateFileName
        
    issuer = 'HogofogoIDP'
    validityInterval = 5    # in minutes
            
    def getLoginResponse(self, request):
        samlReq = self._parseSAMLRequest(request)
        assertion = self._get_saml_assertion(request.user, samlReq)
        return (assertion, samlReq['ACS'])
    

    def _createSubjectElem(self, user, samlReq, notBefore, notOnOrAfter):
        nameId = NameID(format='urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress', 
                        text=user.username)
        scd = SubjectConfirmationData(not_before=notBefore, 
                                      not_on_or_after=notOnOrAfter, 
                                      recipient=samlReq['ACS'], 
                                      in_response_to=samlReq['ID']) 
        sc = SubjectConfirmation('urn:oasis:names:tc:SAML:2.0:cm:bearer',
                                 subject_confirmation_data=scd)
        subject = Subject(name_id=nameId, subject_confirmation=sc)
        return subject
    

    def _createConditionsElem(self, samlReq, notBefore, notOnOrAfter):
        ar = AudienceRestriction(audience=Audience(text=samlReq['ACS']))
        return Conditions(not_before=notBefore, 
                          not_on_or_after=notOnOrAfter, 
                          audience_restriction=ar)
        
    
    def _createAuthnStatementElem(self, user):
        crefStr = 'urn:oasis:names:tc:SAML:2.0:ac:classes:Password'
        ac = AuthnContext(authn_context_class_ref=AuthnContextClassRef(text=crefStr))
        lastLoginGMT = time.strftime("%Y-%m-%dT%H:%M:%SZ", user.last_login.timetuple())
        ass = AuthnStatement(authn_instant=lastLoginGMT, 
                             authn_context=ac)
        return ass
    
    
    def _createSignature(self):
        ref = Reference(uri='', 
                        transforms=Transforms(transform=Transform(algorithm='http://www.w3.org/2000/09/xmldsig#enveloped-signature')), 
                        digest_method=DigestMethod(algorithm='http://www.w3.org/2000/09/xmldsig#sha1'), 
                        digest_value=DigestValue(text=''))
        sInfo = SignedInfo(canonicalization_method=CanonicalizationMethod(algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315#WithComments'), 
                           signature_method=SignatureMethod(algorithm='http://www.w3.org/2000/09/xmldsig#%s-sha1' % 'rsa'), 
                           reference=ref)
        return Signature(signed_info=sInfo, 
                      signature_value=SignatureValue(text=''))
        
        
    def _postProcess(self, assertion):
        """
        Currently sign with the private key and also include the certificate in the SAML response.
        """    
        return sign(str(assertion), self.privateKeyFileName, self.certificateFileName)
    

    def _get_saml_assertion(self, user, samlReqest):
        """
        Return a SAML assertion for the user.
        """ 
        # Create a conditions timeframe (period in which assertion is valid)
        notBefore = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime())
        notOnOrAfter = time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime(time.time() + self.validityInterval))
        
        subject = self._createSubjectElem(user, samlReqest, notBefore, notOnOrAfter)
        conditions = self._createConditionsElem(samlReqest, notBefore, notOnOrAfter)
        authStatement = self._createAuthnStatementElem(user)
    
        # Create the actual assertion
        assertion = Assertion(id=createID(),
                              version='2.0',
                              issue_instant=notBefore, 
                              issuer=Issuer(text=self.issuer),
                              subject=subject, 
                              conditions=conditions, 
                              authn_statement=authStatement)        
        
        response = Response(id=createID(),
                            version='2.0',
                            issue_instant=notBefore, 
                            signature=self._createSignature(), 
                            status=Status(status_code=StatusCode(value='urn:oasis:names:tc:SAML:2.0:status:Success')), 
                            assertion=assertion)

        return self._postProcess(response)
    
    def _b64decodeAndDecompress(self, encodedData):
        decoded_data = base64.b64decode(encodedData)
        return zlib.decompress(decoded_data, -15)

    def _parseSAMLRequest(self, request):
        encodedSamlReq = request.GET.get('SAMLRequest', None)
        samlRequest = self._b64decodeAndDecompress(encodedSamlReq)
        
        reqDOM = parseString(samlRequest)
        req = reqDOM.getElementsByTagName('samlp:AuthnRequest')[0]
        return {
            'ID' : req.attributes['ID'].value,
            'IssueInstant' : req.attributes['IssueInstant'].value,
            'ProviderName' : req.attributes['ProviderName'].value,
            'ACS' : req.attributes['AssertionConsumerServiceURL'].value,
        }