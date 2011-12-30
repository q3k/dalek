import re

class Configuration(object):
    def __init__(self, path):
        f = open(path, "r")
        data_raw = f.read()
        f.close()

        self.data = {}

        for line in data_raw.split("\n"):
            if line.startswith("#"):
                continue

            line = line.strip()
            if line == "":
                continue

            match = re.match("^(?P<key>[^= ]+) ?= ?(?P<value>[^=]+)$", line)
            if not match:
                raise Exception("Could not parse configuration line '%s'!" % line)

            key = match.group("key").strip()
            value = match.group("value").strip()

            self.data[key] = value

    def __getattribute__(self, name):
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            if not name in self.data:
                raise AttributeError("No such config key.")
            return self.data[name]

    def assert_keys(self, keys):
        ok = True
        for key in keys:
            if key not in self.data:
                ok = False
                break
        return ok
