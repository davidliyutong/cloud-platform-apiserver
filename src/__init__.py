from pkg_resources import get_distribution, DistributionNotFound
try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # package is not installed, get git version
    from subprocess import check_output
    try:
        __version__ = check_output(["git", "describe", "--tags", "--abbrev=0"]).strip().decode('utf-8')
    except Exception as e:
        __version__ = ""


# FIXME: this is a hack to make sanic start in fork mode on some linux machines
from sanic import Sanic
Sanic.start_method = 'fork'
Sanic.test_mode = True

# FIXME: this is a hack to disable http warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CONFIG_PROJECT_NAME = "clpl"
CONFIG_BUILD_VERSION = __version__ if __version__ is not None else "v0.0.8"