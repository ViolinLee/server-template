import time
import os
import logging


class DailyLogger:
    def __init__(self, prefix):
        self.prefix = prefix
        self.logger = logging.getLogger(prefix)
        self.logger.setLevel(logging.INFO)  # set log level
        self.format = '[%(asctime)s][%(levelname)s] %(pathname)s %(lineno)d -> %(message)s'  # [%(request_id)s]
        self.suffix = '%Y-%m-%d-0'
        self.cur_handler = None

    def update_handler(self):
        if not os.path.exists('/usr/local/tomcat/logs/'):
            os.makedirs('/usr/local/tomcat/logs/')

        timeTuple = time.localtime()
        logfile = '/usr/local/tomcat/logs/' + self.prefix + time.strftime(self.suffix, timeTuple) + '.log'

        if not os.path.exists(logfile):
            if self.cur_handler is not None:
                self.logger.removeHandler(self.cur_handler)

            # define file handler and set formatter
            self.cur_handler = logging.FileHandler(logfile)
            self.cur_handler.setFormatter(logging.Formatter(self.format))

            # add file handler to logger
            self.logger.addHandler(self.cur_handler)

    def info(self, msg):
        self.update_handler()
        self.logger.info(msg)

    def error(self, msg):
        self.update_handler()
        self.logger.error(msg)


if __name__ == '__main__':
    daily_logger = DailyLogger('normal_roboticscv_server-')
    daily_logger.error("An error message!")
