import logging
import sys

def create_logger():
    # get logger
    logger = logging.getLogger('fastapi-logger')
    
    # clear previous logger
    logger.handlers.clear()

    # create formatter - (determines output format of log records)
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s"
    )

    # create handlers - (determine where the log records get shipped to)
    stream_handler = logging.StreamHandler(sys.stdout) #sends logs for stream handler to standard output
    file_handler = logging.FileHandler('app.log')

    # set formatters
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # add handlers to the logger
    logger.handlers = [stream_handler, file_handler]

    # set log-level
    logger.setLevel(logging.INFO)
    
    return logger

logger = create_logger()