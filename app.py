from ubumlaas import create_monitor, create_app, handler
import signal
import threading

"""
Main, run application.
"""
if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    # create_monitor()
    create_app("main_app").run(host='0.0.0.0', port=8081)