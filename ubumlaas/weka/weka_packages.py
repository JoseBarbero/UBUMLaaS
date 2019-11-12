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
                    print("Installing:",packagename, package_path)
                    packages.install_package(package_path)

    finally:
        jvm.stop()

def uninstall_package(weka_package_name):
    try:
        jvm.start()
        packages.uninstall_package(weka_package_name)
    finally:
        jvm.stop()

def uninstall_unofficial_packages(path):
    try:
        jvm.start()
        with open(path,"r") as f:
            weka_packages = json.load(f)
            for package_name, package_path in weka_packages.items(): 
                if package_name != package_path and packages.is_installed(package_name):
                    print("Uninstalling", package_name)
                    packages.uninstall_package(package_name)
    finally:
        jvm.stop()
                 