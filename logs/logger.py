import os
import sys
import time
import logging
import logging.handlers


class Logger(object):

    _pid = os.getpid()

    def __init__(self):
        # initialize messages to stream
        self._where = 'stderr'
        self._streamhandler = logging.StreamHandler(sys.stderr)
        self._syslog = logging.getLogger()
        self._syslog.setLevel(logging.INFO)
        self._syslog.addHandler(self._streamhandler)
        self._syslog.destination = 'stderr'

        # initialize errors to file
        self._errorhandler = logging.handlers.RotatingFileHandler('/vagrant/bgp-filter/logs/errors.log')
        self._errors = logging.getLogger()
        self._errors.setLevel(logging.ERROR)
        self._errors.addHandler(self._errorhandler)
        self._errors.destination = 'file'

        # initialize debug messages to file
        self._debughandler = logging.handlers.RotatingFileHandler('/vagrant/bgp-filter/logs/debug.log')
        self._debug = logging.getLogger()
        self._debug.setLevel(logging.DEBUG)
        self._debug.addHandler(self._debughandler)
        self._debug.destination = 'file'

    def _format(self, timestamp, level, source, message):
        now = time.strftime('%a, %d %b %Y %H:%M:%S', timestamp)
        return "%s | %-8s | %-6d | %-13s | %s" % (now, level, self._pid, source, message)

    def report(self, message, source='', level=''):
        timestamp = time.localtime()
        if level == 'debug':
            self._debug.debug(self._format(timestamp,
                                           level,
                                           source,
                                           message)
                              )
        elif level == 'info':
            self._syslog.info(self._format(timestamp,
                                           level,
                                           source,
                                           message)
                              )
        elif level == 'warning':
            self._syslog.warn(self._format(timestamp,
                                           level,
                                           source,
                                           message)
                              )
        elif level == "error":
            self._errors.error(self._format(timestamp,
                                            level,
                                            source,
                                            message),
                               exc_info=True
                               )
        elif level == "critical":
            self._errors.critical(self._format(timestamp,
                                               level,
                                               source,
                                               message),
                                  exc_info=True
                                  )

    def debug(self, message, source='', level='debug'):
        self.report(message, source, level)

    def info(self, message, source='', level='info'):
        self.report(message, source, level)

    def warning(self, message, source='', level='warning'):
        self.report(message, source, level)

    def error(self, message, source='', level='error'):
        self.report(message, source, level)

    def critical(self, message, source='', level='critical'):
        self.report(message, source, level)
