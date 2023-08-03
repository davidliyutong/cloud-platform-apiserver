import multiprocessing as mp
import os
import sys

import click
from loguru import logger
from sanic import Sanic

from src.apiserver.server import apiserver_prepare_run, apiserver_check_option
from src.components.config import APIServerConfig, CONFIG_DEFAULT_CONFIG_PATH
from src.components.logging import create_logger
from src.components.tasks import set_crash_flag, get_crash_flag
from src.components.utils import DelayedKeyboardInterrupt

Sanic.start_method = 'fork'

opt: APIServerConfig = APIServerConfig()

if __name__ == '__main__':
    global logger
    # attention: CLPL_LOG_PATH depends on project name
    log_path = os.environ.get('CLPL_LOG_PATH', "./logs/apiserver")
    _ = create_logger(log_path)


    @click.group()
    @click.pass_context
    def cli(ctx):
        pass


    @cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
    @click.pass_context
    def init(ctx):
        """
        Initialize the apiserver with default configuration and environment variables
        """
        import sys
        argv = sys.argv[2:]  # remove the first two arguments
        logger.info("init with args: {}", argv)

        # parse the cli arguments
        args = APIServerConfig.get_cli_parser().parse_args(argv)
        # we need a default config, then patch it with the arguments
        v = APIServerConfig.get_default_config()

        # if config file path is specified in cli arguments , load it with vyper
        if args.config is not None:
            save_path = args.config
            v.set_config_file(args.config)
            try:
                v.read_in_config()
            except Exception as e:
                logger.debug(e)
        else:
            # if not specified, use the default config path
            save_path = CONFIG_DEFAULT_CONFIG_PATH

        # patch the config with cli arguments ( converted to dictionary )
        v.bind_args(vars(args))

        # finally, save the config to the specified path
        err = APIServerConfig.save_config(v, path=save_path)
        if err is not None:
            logger.error(err)
        return None


    @cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
    @click.pass_context
    def serve(ctx):
        global opt
        with DelayedKeyboardInterrupt():
            # parse the cli arguments using vyper, then build option from vyper
            v, err = APIServerConfig.load_config(argv=sys.argv[2:])
            opt = APIServerConfig().from_vyper(v)
            logger.info(f"running option: {opt.to_dict()}")  # TODO: adapt logging level to DEBUG variable

            # prepare and run the server
            app = apiserver_prepare_run(apiserver_check_option(opt))
            app.config.update_config(opt.to_sanic_config())

        try:
            app.run(host=opt.api_host,
                    port=opt.api_port,
                    access_log=opt.api_access_log,
                    workers=opt.api_num_workers if opt.api_access_log > 0 else mp.cpu_count(),
                    auto_reload=False)
        except KeyboardInterrupt as _:
            logger.info("KeyboardInterrupt, terminating workers")
            sys.exit(1)


    cli()
