import os
import sys

import click
import sanic
from loguru import logger

from src.components.config import APIServerConfig, CONFIG_PROJECT_NAME
from src.components.logging import create_logger
from src.components.utils import DelayedKeyboardInterrupt
from src.rbacserver.server import rbac_server_prepare_run, rbac_server_check_option

opt: APIServerConfig = APIServerConfig()

if __name__ == '__main__':
    global logger
    log_path = os.environ.get(f'{CONFIG_PROJECT_NAME.upper()}_RBAC_LOG_PATH', "logs/rbac/")
    log_debug_flag = bool(os.environ.get(f'{CONFIG_PROJECT_NAME.upper()}_DEBUG', "false") in ["1", "True", "true"])
    _ = create_logger(log_path, log_debug_flag)


    @click.group()
    @click.pass_context
    def cli(ctx):
        pass


    @cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
    @click.pass_context
    def serve(ctx):
        global opt
        with DelayedKeyboardInterrupt():
            # parse the cli arguments using vyper, then build option from vyper
            v, err = APIServerConfig.load_config(argv=sys.argv[2:])
            opt = APIServerConfig().from_vyper(v)
            # disable output on release version to avoid leaking sensitive information
            logger.debug(f"running option: {opt.model_dump()}")

            # prepare and run the rbacserver server
            app = rbac_server_prepare_run(rbac_server_check_option(opt))

            # notice: the app will handle keyboard interrupt
            try:
                # qps: 7280 when using 4 workers /v1/enforce and basic rules
                # qps: 47743 when using 4 workers /v1/healtz
                app.run(host="127.0.0.1",
                        port=opt.rbac_port,
                        access_log=opt.rbac_access_log,
                        single_process=True if opt.rbac_num_workers == 1 else False,
                        workers=opt.rbac_num_workers,
                        auto_reload=False,
                        debug=opt.debug)
            except sanic.exceptions.ServerKilled as e:
                sys.exit(0)

            except Exception as e:
                logger.error(f"unknown err: {e}")
                sys.exit(1)


    cli()
