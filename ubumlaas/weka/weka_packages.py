import weka.core.jvm as jvm
import weka.core.packages as packages
import json

def install_packages(path):
    """Install weka packages
    
    Arguments:
        path {str} -- path to install weka packages json
    """

    try:
        
        with open(path,"r") as f:
            jvm.start()
            weka_packages = json.load(f)
            for package_name, package_path in weka_packages.items(): 
                if not packages.is_installed(package_name):
                    print("Installing:", package_path)
                    packages.install_package(package_path)

    finally:
        jvm.stop()

def uninstall_package(weka_package_name):
    try:
        jvm.start()
        packages.uninstall_package(weka_package_name)
    finally:
        jvm.stop()
