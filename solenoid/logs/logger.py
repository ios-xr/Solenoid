import os
import time
import sys
import logging
import logging.handlers


class PermissiveRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def _open(self):
        prevumask = os.umask(0002)
        rfh_open = logging.handlers.RotatingFileHandler._open(self)
        os.umask(prevumask)
        return rfh_open


class Logger(object):

    _pid = os.getpid()
    _location = os.path.dirname(os.path.realpath(__file__))
    logging.handlers.PermissiveRotatingFileHandler = PermissiveRotatingFileHandler

    def __init__(self):

        self._logger = logging.getLogger()
        self._logger.setLevel(logging.DEBUG)
        # initialize messages to stream
        self._streamhandler = logging.StreamHandler(sys.stderr)
        self._streamhandler.setLevel(logging.INFO)
        self._logger.addHandler(self._streamhandler)
        # initialize errors to file
        err_filepath = os.path.join(self._location, 'errors.log')
        self._errorhandler = logging.handlers.PermissiveRotatingFileHandler(
            err_filepath
        )
        self._errorhandler.setLevel(logging.ERROR)
        self._logger.addHandler(self._errorhandler)
        # initialize debug messages to file
        deb_filepath = os.path.join(self._location, 'debug.log')
        self._debughandler = logging.handlers.PermissiveRotatingFileHandler(
            deb_filepath
        )
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
