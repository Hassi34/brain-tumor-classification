import logging
import logging.handlers

def get_logger(logsFilePath: str, maxBytes: int=10240000000000, backupCount: int=0) -> object:
    logger = logging.getLogger()
    fh = logging.handlers.RotatingFileHandler(logsFilePath, maxBytes=maxBytes, backupCount=backupCount)
    fh.setLevel(logging.DEBUG)#no matter what level I set here
    formatter = logging.Formatter("[%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(lineno)s] : %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    return logger
