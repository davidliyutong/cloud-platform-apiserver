import os
import sys
sys.path.extend([
    os.path.abspath("./src/clients/rbac_client"),
])

import click
import sanic
from loguru import logger

from src.apiserver.server import apiserver_prepare_run, apiserver_check_option
from src.components.config import APIServerConfig, CONFIG_DEFAULT_CONFIG_PATH, CONFIG_PROJECT_NAME
from src.components.logging import create_logger
from src.components.utils import DelayedKeyboardInterrupt

opt: APIServerConfig = APIServerConfig()

if __name__ == '__main__':
    global logger
    log_path = os.environ.get(f'{CONFIG_PROJECT_NAME.upper()}_LOG_PATH', "./logs/apiserver")
    log_debug_flag = bool(os.environ.get(f'{CONFIG_PROJECT_NAME.upper()}_DEBUG', "false") in ["1", "True", "true"])
    _ = create_logger(log_path, log_debug_flag)


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
            # disable output on release version to avoid leaking sensitive information
            logger.debug(f"running option: {opt.model_dump()}")

            # prepare and run the server
            app = apiserver_prepare_run(apiserver_check_option(opt))

            # notice: the app will handle keyboard interrupt
            try:
                app.run(host=opt.api_host,
                        port=opt.api_port,
                        access_log=opt.api_access_log,
                        single_process=True if opt.api_num_workers == 1 else False,
                        workers=opt.api_num_workers,
                        auto_reload=False,
                        debug=opt.debug)
            except sanic.exceptions.ServerKilled as e:
                sys.exit(0)

            except Exception as e:
                logger.error(f"unknown err:R {e}")
                sys.exit(1)


    cli()
