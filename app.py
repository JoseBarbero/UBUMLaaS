from ubumlaas import create_app
import signal
import threading
import sys

"""
Main, run application.
"""
if __name__ == "__main__":
    try:
        host = sys.argv[1] 
    except IndexError:
        host='localhost'
    try:
        port = sys.argv[2]
    except IndexError:
        port = 5000

    create_app("main_app").run(host=host, port=port)