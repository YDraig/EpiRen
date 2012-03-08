from distutils.core import setup
import py2exe

setup(
    options = {'py2exe': {'bundle_files': 2, "dll_excludes": ["w9xpopen.exe"]}},
    windows = [
        {
            "script": "EpiRen.pyw",
            "icon_resources": [(0,"EpiRen.ico")],
        },
    ],
    data_files=[('', ["msvcm90.dll", "msvcp90.dll", "msvcr90.dll", "Microsoft.VC90.CRT.manifest"])],
    name="EpiRen",
    version="1.4",
    author="Brinley Craig",
    description="Episode Renaming Utility",
    #zipfile = None
) 