from restClient import RestCalls


class JSONRestCalls(RestCalls):
    Format = 'json'

    def __repr__(self):
        return '%s(Session Object%s, Host = %s, Format = %s)' % (
            self.__class__.__name__,
            self._session.headers.items(),
            self._host,
            self.Format
        )
