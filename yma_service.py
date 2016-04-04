__author__ = 'namhyun'
import webapp2
from lxml import html
import xml.etree.cElementTree as etree
from urlbuilder import urlbuilder
from google.appengine.api import urlfetch

class Type(object):
    Meal = 2
    Kcal = 17
    Carbohydrate = 18
    Protein = 19
    Fat = 20

    def __init__(self):
        super(Type, self).__init__()

class ResultCode(object):
    Successful = 100
    UnCompleteResultException = 101
    WrongParameterException = 102

    def __init__(self):
        super(ResultCode, self).__init__()


class YmaServiceHandler(webapp2.RedirectHandler):
    REQUIRE_PARAMETER = ["CountryCode", "schulCode", "schulCrseScCode", "schulKndScCode", "schMmealScCode"]

    # urlfetch deadline config
    URLFETCH_DEADLINE = 50

    def get(self):
        request_parameter_result = []
        for param in self.REQUIRE_PARAMETER:
            request_parameter_result.append(self.request.get(param))
        self.request_data(request_parameter_result)

    def request_data(self, parameters):
        base_url = "http://hes." + parameters[0]
        builder = urlbuilder(base_url)
        builder.append_path("sts_sci_md01_001.do")
        for index in range(1, 4):
            builder.append_query_param(self.REQUIRE_PARAMETER[index], parameters[index])
        built_url = builder.build()

        server_response = urlfetch.fetch(built_url, deadline=self.URLFETCH_DEADLINE)
        server_content = unicode(server_response.content, "utf-8")
        content_document = html.document_fromstring(server_content)
        content_document.make_links_absolute(built_url)


