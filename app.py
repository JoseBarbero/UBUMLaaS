from ubumlaas import create_app
import signal
import threading

"""
Main, run application.
"""
if __name__ == "__main__":
    create_app("main_app").run(host='0.0.0.0', port=8081)