import sys
import importlib


if __name__ == "__main__":
    arg = sys.argv[1]
    scriptModule = importlib.import_module("Integrations." + arg)

    script_class = getattr(scriptModule, arg)
    scriptInstance = script_class()

    scriptInstance.scrape()
