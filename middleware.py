from suds.client import Client
from suds import WebFault
from django.conf import settings
from django.http import HttpResponse
import logging
from xml.dom import minidom

class WAPLMiddleware(object):
    """
    A Django middleware class that mobilises an existing Django app
    with miminal effort. 
    
    It integrates with the WAPL markup language provided by Wapple.net,
    via SOAP calls.
    
    Please see http://wapl.info for more information.
    """
    
    url = 'http://webservices.wapple.net/wapl.wsdl'
    dev_key = 'Wapple'
    session_var_name = 'is_mobile'
    template_sub_dir = 'wapl'
    is_mobile = False
    
    def __init__(self):
        ##
        ##   Uncomment the below lines to print SOAP messages to the console.
        ##   Useful for debugging SOAP errors.
        ##
        #logging.basicConfig(level=logging.INFO)
        #logging.getLogger('suds.client').setLevel(logging.DEBUG)
        self.init_client()
    
    def handle_request_error(self, error, request):
        """
        Handles any SOAP errors sent back from the SOAP server during the
        process_request function.
        """
        ##
        ##    Your error handling goes here.
        ##    
        ##    This should return an HttpResponse object or
        ##    None to continue processing the request
        ##
        ##
        raise error

    def handle_response_error(self, error, request, response):
        """
        Handles any SOAP errors sent back from the SOAP server during the
        process_response function.
        """
        ##
        ##    Your error handling goes here.
        ##    
        ##    This should return an HttpResponse object or
        ##    None to continue processing the request
        ##
        ##
        raise error

    def init_client(self):
        """
        Initialises the SOAP client.
        """
        self.client = Client(self.url)   
    
    def append_td(self, td):
        """
        Ammends a template directory setting to the wapl version.
        """
        if td[(-1-len(self.template_sub_dir)):] == '%s/' % self.template_sub_dir:
            return td
        if td[-1] != '/':
            td = td + '/'
        return td + '%s/' % self.template_sub_dir
    
    def restore_td(self, td):
        """
        Restores the template directory setting ready for the next request
        """
        if td[(-1-len(self.template_sub_dir)):] == '%s/' % self.template_sub_dir:
            return td[:-5]
	else:
	    return td
    
    def build_headers(self,request):
        """
        Builds the request headers into the appropriate form to 
        post to the SOAP call.
        """
        headers = self.client.factory.create('deviceHeaders')
        for name, val in request.META.items():
            item = self.client.factory.create('deviceItem')
            item.name = name
            item.value = val
            headers.deviceItem.append(item)   
        return headers 
                
    def process_request(self,request):   
        """
        Checks if the device is a mobile device by:
        
        1. Checking if the user has 'is_mobile' in their session.
        2. Calling the WAPL web service.
        
        If the device is not mobile, it does nothing, otherwise
        it modifies the TEMPLATE_DIRECTORIES setting to look for templates
        in a wapl/ subfolder.
        """     
	if self.session_var_name in request.session:
            self.is_mobile = request.session[self.session_var_name] == 'True'
        else:
            self.init_client()
            try:
                self.is_mobile = self.client.service.isMobileDevice(self.dev_key,self.build_headers(request)) == '1'
            except WebFault, w:
                return self.handle_request_error(w, request)
            request.session[self.session_var_name] = str(self.is_mobile)
                   
        if self.is_mobile:
            settings.TEMPLATE_DIRS = tuple([self.append_td(td) for td in settings.TEMPLATE_DIRS])
                        
    def process_response(self,request,response):
        """        
        If the device is mobile, and the response code is OK,
        it generates the correct markup for the requesting device by
        calling the WAPL web service.
        
        Otherwise, it returns the response untouched.
        """

        settings.TEMPLATE_DIRS = tuple([self.restore_td(td) for td in settings.TEMPLATE_DIRS])                  

        if response.status_code != 200 or self.DEBUG_WAPL:
            return response
        
        if self.is_mobile:
            self.is_mobile = False
            
            self.init_client()
            wapl = response.content
            try:
                wapl_response = self.client.service.getMarkupFromWapl(self.dev_key,wapl,self.build_headers(request))
            except WebFault, w:
                return self.handle_response_error(w,request,response)
            
            doc = minidom.parseString(wapl_response)
            markup = doc.getElementsByTagName('markup')[0].childNodes[1].data
            return HttpResponse(markup)            
        else:
            return response 
