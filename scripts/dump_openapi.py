"""
Boot the Sanic API server, scrape /docs/openapi.json, and write it to disk.

Intended for CI: stubs out MongoDB / Kubernetes so we don't need real
dependencies to render the OpenAPI document.

Usage:
    python -m scripts.dump_openapi --output openapi.json --port 8080
"""
import argparse
import asyncio
import http.client
import json
import os
import signal
import sys
import threading
import time


# --- bypass external dependencies (db, k8s) -----------------------------------
# Patches MUST happen before the apiserver modules are imported, because
# `apiserver_prepare_run` calls into these at module load.

async def _async_none(*_a, **_kw):
    return None


async def _async_get_crash_flag(*_a, **_kw):
    return False, None


async def _async_recover(*_a, **_kw):
    return True, None


async def _async_scan(*_a, **_kw):
    return None


class _K8sStub:
    def __getattr__(self, _name):
        return _K8sStub()

    def __call__(self, *_a, **_kw):
        return _K8sStub()


# Import the server module first so the dependency graph (tasks -> controller
# -> tasks) initializes cleanly, then overwrite the symbols we need to stub.
import src.apiserver.server.server as _srv  # noqa: E402
import src.apiserver.controller.controller as _ctrl  # noqa: E402
import src.components.tasks as _tasks  # noqa: E402
import src.components.utils as _utils  # noqa: E402

_tasks.check_and_create_admin_user = lambda _opt: None
_tasks.check_kubernetes_connection = lambda _opt: None
_tasks.set_crash_flag = _async_none
_tasks.get_crash_flag = _async_get_crash_flag
_tasks.recover_from_crash = _async_recover
_tasks.scan_pods = _async_scan

_utils.get_k8s_client = lambda *_a, **_kw: _K8sStub()

_ctrl.set_crash_flag = _async_none
_ctrl.get_crash_flag = _async_get_crash_flag
_ctrl.recover_from_crash = _async_recover
_ctrl.scan_pods = _async_scan

_srv.check_and_create_admin_user = lambda _opt: None
_srv.check_kubernetes_connection = lambda _opt: None
_srv.get_k8s_client = lambda *_a, **_kw: _K8sStub()


# --- start the app and fetch the spec ----------------------------------------

from sanic import Sanic  # noqa: E402

from src.apiserver.server.server import (  # noqa: E402
    apiserver_check_option,
    apiserver_prepare_run,
)
from src.components.config import APIServerConfig  # noqa: E402


def _fetch_spec(host: str, port: int, output: str, timeout_s: int) -> int:
    deadline = time.time() + timeout_s
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            conn = http.client.HTTPConnection(host, port, timeout=2)
            conn.request("GET", "/docs/openapi.json")
            resp = conn.getresponse()
            if resp.status == 200:
                spec = json.loads(resp.read())
                with open(output, "w") as f:
                    json.dump(spec, f, indent=2, sort_keys=True)
                print(f"openapi.json written to {output} ({os.path.getsize(output)} bytes)")
                return 0
            last_err = RuntimeError(f"HTTP {resp.status}")
        except Exception as e:  # noqa: BLE001
            last_err = e
        time.sleep(0.5)
    print(f"timed out fetching openapi.json: {last_err}", file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="openapi.json")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--timeout-s", type=int, default=30)
    args = parser.parse_args()

    Sanic.start_method = "fork"
    Sanic.test_mode = True

    opt = APIServerConfig()
    opt.api_host = args.host
    opt.api_port = args.port
    # `opt.verify()` requires these to be non-empty.
    opt.config_workspace_hostname = "openapi.local"
    opt.config_workspace_tls_secret = "openapi-tls"
    opt.config_auth_endpoint = "http://localhost"
    opt.config_token_secret = "openapi-dump-secret"
    # Enable OIDC so its blueprint is registered and appears in the spec.
    # The four fields below are required by opt.verify() when OIDC is on.
    opt.config_use_oidc = True
    opt.oidc_frontend_login_url = "http://localhost/login"
    opt.oidc_client_id = "openapi-dump"
    opt.oidc_client_secret = "openapi-dump-secret"
    opt.oidc_redirect_url = "http://localhost/callback"

    app = apiserver_prepare_run(apiserver_check_option(opt))
    app.config.update_config(opt.to_sanic_config())

    # The controller's after_server_start / before_server_stop listeners and
    # Sanic itself look at `application.m.*`, but the multiplexer only exists
    # in multi-worker mode. Install a stub so single_process mode works.
    class _MStub:
        name = "openapi-dump"

        def __getattr__(self, _name):
            return lambda *_a, **_kw: None

    type(app).multiplexer = property(lambda _self: _MStub())

    exit_code: dict[str, int] = {"code": 1}

    def _worker():
        try:
            exit_code["code"] = _fetch_spec(args.host, args.port, args.output, args.timeout_s)
        finally:
            os.kill(os.getpid(), signal.SIGINT)

    threading.Thread(target=_worker, daemon=True).start()

    try:
        app.run(
            host=args.host,
            port=args.port,
            single_process=True,
            access_log=False,
            auto_reload=False,
            debug=False,
        )
    except (KeyboardInterrupt, SystemExit):
        pass

    return exit_code["code"]


if __name__ == "__main__":
    sys.exit(main())
