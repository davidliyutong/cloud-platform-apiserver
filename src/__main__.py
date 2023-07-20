from src.components.config import BackendConfig
from src.apiserver.server import prepare_run
from loguru import logger
import click
from sanic import Sanic

Sanic.start_method = 'fork'

opt: BackendConfig = BackendConfig()

if __name__ == '__main__':
    global logger


    @click.group()
    @click.pass_context
    def cli(ctx):
        pass


    @cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
    @click.pass_context
    def init():
        import sys
        argv = sys.argv[2:]
        logger.info("init with args: {}", argv)
        args = BackendConfig.get_cli_parser().parse_args(argv)
        v = BackendConfig.get_default_config()
        if args.config is not None:
            v.set_config_file(args.config)
            try:
                v.read_in_config()
            except Exception as e:
                logger.debug(e)
        v.bind_args(vars(args))

        err = BackendConfig.save_config(v, path=args.config)
        if err is not None:
            logger.error(err)
        return None


    @cli.command(context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
    @click.pass_context
    def serve(ctx):
        global opt
        v, err = BackendConfig.load_config(argv=[])
        opt = BackendConfig().from_vyper(v)
        logger.info(f"running option: {opt.to_dict()}")
        app = prepare_run(opt)
        app.config.update_config(opt.to_sanic_config())
        app.run(host=opt.api_host,
                port=opt.api_port,
                access_log=opt.api_access_log,
                workers=opt.api_num_workers,
                auto_reload=False)


    cli()
