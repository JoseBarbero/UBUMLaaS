import logging as log
import json
import os
import variables as v

log.OP = 1
log.addLevelName(log.OP, "OP")


def operationv(self, *args, **kwargs):
    message = ";".join(map(str, args))
    self._log(log.OP, "%s", message, **kwargs)


log.Logger.operation = operationv


class OpHandler(log.FileHandler):
    def __init__(self, *args, **kwargs):
        log.FileHandler.__init__(self, *args, **kwargs)
        self.addFilter(OPFilter())


class OPFilter(log.Filter):

    def filter(self, x):
        return x.levelno == log.OP


def create_folders_if_needed():
    with open(os.path.join(v.appdir, "logging_config.json"), "r") as fil:
        logging_conf = json.load(fil)
    for hd in logging_conf["handlers"]:
        if "filename" in logging_conf["handlers"][hd]:
            os.makedirs(
                os.path.dirname(
                    os.path.join(
                        v.appdir,
                        logging_conf["handlers"][hd]["filename"])),
                exist_ok=True)
