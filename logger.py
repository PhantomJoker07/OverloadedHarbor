import logging

#logging.basicConfig(filename='debug.log',level=logging.DEBUG)  #UNCOMMENT THIS FOR LOGGING

logger = logging.getLogger(__name__)

def debug_log(_id,message=''):
    msg = str(_id) + ":: " + str(message)
    logging.debug(msg)

def error_log(message):
    logging.error(message)

def clear_log():
    with open('debug.log', 'wb') as fd:
        fd.write(b'')