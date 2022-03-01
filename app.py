from ubumlaas import create_app, handler
import signal

"""
Main, run application.
"""
if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)