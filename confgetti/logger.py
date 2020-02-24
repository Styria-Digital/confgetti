import logging


class DuplicateFilter(logging.Filter):
    """
    Logging filter for removing duplicate messages for stdout
    """
    def filter(self, record):
        """
        Compare incoming message with last log and if they are not same,
        return True which indicates that message should be displayed.

        :param record: message record
        :type record: string

        :returns: boolean indicating if message should be displayed or no
        :rtype: boolean
        """
        current_log = (record.module, record.levelno, record.msg)

        if current_log != getattr(self, "last_log", None):
            self.last_log = current_log
            return True

        return False
