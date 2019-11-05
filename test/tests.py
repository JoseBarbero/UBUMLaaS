from test.test_case.test_execute_algorithm import ExecuteLibsTest, ParametrizedTestCase
import unittest
from ubumlaas import create_app
import glob
import weka.core.jvm as jvm


def suite_execute_algorithm():
        filenames = glob.glob("test/json/*.json")
        results = []
        for filename in filenames:
                print("\n\n\nTesting:", filename)
                suite = unittest.TestSuite()
                suite.addTest(ParametrizedTestCase.parametrize(ExecuteLibsTest, param = filename))
                result = unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
                results.append(result.wasSuccessful())
        return results
        

if __name__ == "__main__":
        try:
                results=[]
                create_app("subprocess")
                jvm.start(packages=True)
                results+=suite_execute_algorithm()
        finally:
                
                jvm.stop()

        exit(results.count(False))