import re

from lxml import etree as ET
from exceptions import YangFileException
from rest.restClass import RestCalls


class XMLRestCalls(RestCalls):
    Format = 'xml'

    def _get_endpoint(self, data):
        """Check the data's type and the YANG model

            :param data_source: The JSON or XML
            :type data_source: str
            :return: Returns the type of data in the file and the
                     yang model name and local name
            :rtype: tuple(string, string)

        """
        xml_data = ET.fromstring(data)
        namespace_uri = xml_data.xpath('namespace-uri(.)')
        local_name = xml_data.xpath('local-name()')
        if namespace_uri and local_name:
            namespace = re.search(r'[^/]+$', namespace_uri).group(0)
            return(namespace + ':' + local_name)
        else:
            raise YangFileException('XML file requires the YANG namespace')
