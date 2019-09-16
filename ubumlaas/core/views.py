from flask import render_template, request, Blueprint
from ubumlaas import celery

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
    @celery.task(name='tasks.async_run_get_manifest')
    def run_get_manifest():
        """ Run the entire get_manifest flow as a single function """
        print("Vamos a intentarlo")
        build_path()
        manifest_version = request_manifest_version()
        if check_manifest(manifest_version) is True:
            getManifest()
            buildTable()
            manifest_type = "full"
            all_data = buildDict(DB_HASH)
            writeManifest(all_data, manifest_type)
            cleanUp()
            print("Conseguido")
        else:
            print("No change detected!")
    
        return
    run_get_manifest.delay()
    return
