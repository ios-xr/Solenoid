import os
import sys
import time
import logging
import logging.handlers


class Logger(object):

    _pid = os.getpid()

    def __init__(self):

        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        # initialize messages to stream
        self._streamhandler = logging.StreamHandler(sys.stderr)
        self._streamhandler.setLevel(logging.INFO)
        self._logger.addHandler(self._streamhandler)
        # initialize errors to file
        self._errorhandler = logging.handlers.RotatingFileHandler(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'errors.log'))
        self._errorhandler.setLevel(logging.ERROR)
        self._logger.addHandler(self._errorhandler)

        # initialize debug messages to file
        self._debughandler = logging.handlers.RotatingFileHandler(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'debug.log'))
        self._debughandler.setLevel(logging.DEBUG)
        self._logger.addHandler(self._debughandler)

    def _format(self, timestamp, level, source, message):
        now = time.strftime('%a, %d %b %Y %H:%M:%S', timestamp)
        return "%s | %-8s | %-6d | %-13s | %s" % (now, level, self._pid, source, message)

    def report(self, message, source='', level=''):
        timestamp = time.localtime()
        if level == 'DEBUG':
            self._logger.debug(self._format(timestamp,
                                            level,
                                            source,
                                            message)
                               )
        elif level == 'INFO':
            self._logger.info(self._format(timestamp,
                                           level,
                                           source,
                                           message)
                              )
        elif level == 'WARNING':
            self._logger.warn(self._format(timestamp,
                                           level,
                                           source,
                                           message)
                              )
        elif level == "ERROR":
            self._logger.error(self._format(timestamp,
                                            level,
                                            source,
                                            message),
                               exc_info=True
                               )
        elif level == "CRITICAL":
            self._logger.critical(self._format(timestamp,
                                               level,
                                               source,
                                               message),
                                  exc_info=True
                                  )

    def debug(self, message, source='', level='DEBUG'):
        self.report(message, source, level)

    def info(self, message, source='', level='INFO'):
        self.report(message, source, level)

    def warning(self, message, source='', level='WARNING'):
        self.report(message, source, level)

    def error(self, message, source='', level='ERROR'):
        self.report(message, source, level)

    def critical(self, message, source='', level='CRITICAL'):
        self.report(message, source, level)
