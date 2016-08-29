"""main
"""
import argparse
import sys
import nmzswarm
from nmzswarm.driver.docker import DockerDriver
from nmzswarm.driver.driver import Driver
from nmzswarm.driver.k8s import KubernetesDriver
from nmzswarm.logstorage.file import FileLogStorage
from nmzswarm.progress.progress import ProgressUI
from nmzswarm.progress.simple import SimpleProgressUI
from nmzswarm.progress.standard import StandardProgressUI
from nmzswarm.run import run
from nmzswarm.scheduler.naive import NaiveScheduler

LOG = nmzswarm.LOG.getChild(__name__)


def _init_db(args: argparse.Namespace) -> None:
    LOG.debug('using db %s', args.db)
    raise NotImplementedError


def _ui(name: str) -> ProgressUI:
    if name == 'standard':
        return StandardProgressUI()
    elif name == 'simple':
        return SimpleProgressUI()
    raise RuntimeError('unsupported ui %s' % name)


def _driver(name: str) -> Driver:
    if name == 'docker':
        return DockerDriver()
    elif name == 'k8s':
        return KubernetesDriver()
    raise RuntimeError('unsupported driver %s' % name)


def _run(args: argparse.Namespace) -> None:
    if len(args.image) != 1:
        raise RuntimeError('only single image is supported, got %s'
                           % args.image)
    image = args.image[0]
    driver = _driver(args.driver)
    storage = FileLogStorage(args.logs)
    scheduler = NaiveScheduler()
    ui = _ui(args.ui)
    run(driver, scheduler, storage, ui,
        args.parallel, image)


def _create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='nmzswarm',
        description='CI Job Parallelizer built on Docker and Kubernetes')
    parser.add_argument('-d', '--driver',
                        choices=['docker', 'k8s'],
                        default='docker',
                        help='Orchestration driver')
    parser.add_argument('--db',
                        type=str,
                        help='DB connection string ' +
                        '(e.g. "sqlite:///nmzswarm.sqlite3")')

    def _default_func(_args: argparse.Namespace) -> None:
        parser.print_help()
        parser.exit(1)
    parser.set_defaults(func=_default_func)

    subparsers = parser.add_subparsers()
    parser_init_db = subparsers.add_parser('init-db', help='Initialize the DB')
    parser_init_db.set_defaults(func=_init_db)

    parser_run = subparsers.add_parser(
        'run', help='Run jobs in parallel across the cluster')
    parser_run.add_argument('--ui',
                            choices=['standard', 'simple'],
                            default='standard',
                            help='Progress UI')
    parser_run.add_argument('--parallel',
                            type=int,
                            default=1,
                            help='Number of jobs executed in parallel')
    parser_run.add_argument('--logs',
                            type=str,
                            required=True,
                            help='Path to the directly which contains logs')
    parser_run.add_argument('image',
                            nargs='+',
                            help='Image that contains NamazuSwarmfile')
    parser_run.set_defaults(func=_run)
    return parser


def _main() -> int:
    parser = _create_parser()
    args = parser.parse_args()
    args.func(args)
    return 0

if __name__ == '__main__':
    sys.exit(_main())
