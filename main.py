import sys
import importlib

if __name__ == "__main__":
    arg = sys.argv[1]
    scriptModule = importlib.import_module("Services." + arg)

    script_class = getattr(scriptModule, arg)
    scriptInstance = script_class(True)
    scriptInstance.setup()
    scriptInstance.main()
