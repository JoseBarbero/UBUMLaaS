import weka.core.jvm as jvm
import weka.core.packages as packages
import json
import variables as v

def install_packages(path):
    """Install weka packages

    Arguments:
        path {str} -- path to install weka packages json
    """

    with open(path, "r") as f:
        weka_packages = json.load(f)
        for package_name, package_path in weka_packages.items(): 
            if not packages.is_installed(package_name):
                v.app.logger.info("Installing: %s %s", package_name, package_path)
                packages.install_package(package_path)


def uninstall_package(weka_package_name):
    try:
        jvm.start()
        packages.uninstall_package(weka_package_name)
    finally:
        jvm.stop()


def uninstall_unofficial_packages(path):
    with open(path,"r") as f:
        weka_packages = json.load(f)
        for package_name, package_path in weka_packages.items(): 
            if package_name != package_path and packages.is_installed(package_name):
                v.app.logger.info("Uninstalling %s", package_name)
                packages.uninstall_package(package_name)



def start_up_weka(path):
    try:
        jvm.start()

        uninstall_unofficial_packages(path)
        install_packages(path)
    finally:
        jvm.stop()