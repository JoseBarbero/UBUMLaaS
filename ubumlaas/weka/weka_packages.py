import weka.core.jvm as jvm
import weka.core.packages as packages

def install_packages(path):

    try:
        
        with open(path,"r") as f:
            jvm.start()
            lines=f.readlines()
            for line in lines: 
                if not packages.is_installed(line):
                    packages.install_package(line)

    finally:
        jvm.stop()
        