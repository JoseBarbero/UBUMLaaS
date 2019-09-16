from flask import render_template, request, Blueprint
import variables as v
import time

core = Blueprint('core', __name__)

@core.route('/')
def index():
    return render_template('index.html', title="UBUMLaaS")

@core.route('/info')
def info():
    return render_template('info.html', title="Information")

@core.route('/launcher')
def task_launcher():
    return render_template('launch_tasks.html', title="Task Launcher")

@core.route('/launcher_ajax', methods=["POST"])
def ajax_tasks():
     
    req = request.get_json()
    if req["op"] == "start":
        job = v.q.enqueue(background_task, req["proc"], req["time"])

    return ""

def background_task(name,tim):

        """ Function that returns len(n) and simulates a delay """

        delay = int(tim)

        print("Task running")
        print(f"Simulating a {delay} second delay")

        time.sleep(delay)

        print(len(name))
        print("Task complete")

        return len(name)