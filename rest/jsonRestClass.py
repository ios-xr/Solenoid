import json
import re

from exceptions.exceptions import YangFileException
from rest.restClass import RestCalls


class JSONRestCalls(RestCalls):
    Format = 'json'

    def _get_endpoint(self, data):
        """Check the data's type and the YANG model

            :param data_source: The JSON or XML
            :type data_source: str
            :return: Returns the type of data in the file and the
                     yang model name and local name
            :rtype: tuple(string, string)

        """
        context = json.loads(data)
        yang_selection = context.keys()[0]
        match = re.search(r':', yang_selection)
        if match:
            return yang_selection
        else:
            raise YangFileException('Yang module name required in file')
