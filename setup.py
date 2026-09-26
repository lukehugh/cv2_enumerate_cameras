import sys
import sysconfig

from setuptools import Extension, setup


ext_modules = []
options = {}

if sys.platform == "win32":
    limited_api = not sysconfig.get_config_var("Py_GIL_DISABLED")
    ext_modules.append(
        Extension(
            name="cv2_enumerate_cameras._windows_backend",
            sources=["cv2_enumerate_cameras/_windows_backend.cpp"],
            py_limited_api=limited_api,
            define_macros=[("Py_LIMITED_API", "0x030A0000")] if limited_api else [],
        )
    )
    if limited_api:
        options["bdist_wheel"] = {"py_limited_api": "cp310"}

setup(ext_modules=ext_modules, options=options)
