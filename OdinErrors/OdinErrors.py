import sublime, sublime_plugin

import os
import re
import json
import shutil
import subprocess

class OdinErrors(sublime_plugin.EventListener):
    def on_post_save_async(self, view):
        if os.path.splitext(view.file_name())[1] != ".odin": return

        os.chdir(sublime.active_window().extract_variables()["folder"])

        res = list(filter(lambda x: x[0] != "\t", self.odin_check_res(view, self.load_ols_file(view))))

        lines = []
        anos  = []

        for i in res:
            l, c = map(
                int,
                re.findall("\([0-9]*:[0-9]*\) ", i)[0][1:-2].split(":")
            )

            ul = view.line(view.text_point(l - 1, 0))
            ul.a += c - 1

            lines.append(ul)
            anos.append(re.split("\([0-9]*:[0-9]*\) ", i)[1])

        view.add_regions("odin errors", lines, "region.redish", "", sublime.DRAW_STIPPLED_UNDERLINE | sublime.DRAW_NO_FILL | sublime.DRAW_NO_OUTLINE, anos)

    def odin_check_res(self, view, args):
        sinfo = None

        if os.name == "nt":
            sinfo = subprocess.STARTUPINFO()
            sinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        return list(filter(
            lambda x: x.startswith(view.file_name().replace("\\", "/")),
            subprocess.Popen(
                [shutil.which("odin"), "check", os.path.dirname(view.file_name()), "-no-entry-point"] + args,
                stdout = subprocess.PIPE,
                stderr = subprocess.STDOUT,
                startupinfo = sinfo
            ).communicate()[0].decode("utf-8").split("\n")[:-1]
        ))

    def load_ols_file(self, view):
        try:
            f = json.loads(open("./ols.json", "r").read())
        except:
            return []

        return list(map(
            lambda x: "-collection:" + x["name"] + "=" + x["path"],
            filter(
                lambda x: x["name"] != "core" and x["name"] != "vendor", 
                f["collections"]
            )
        )) + list(map(
            lambda x: "-define:" + x["name"] + "=" + x["value"],
            f["defines"]
        ))
