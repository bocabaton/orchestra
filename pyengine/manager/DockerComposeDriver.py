import os
import requests
import uuid

import contextlib
import functools
import json
import logging
import re
import sys
from inspect import getdoc
from operator import attrgetter

from compose.cli import errors
from compose.cli import signals
from compose import __version__
from compose.config import config
from compose.config import ConfigurationError
from compose.config import parse_environment
from compose.config.environment import Environment
from compose.config.serialize import serialize_config
from compose.const import DEFAULT_TIMEOUT
from compose.const import IS_WINDOWS_PLATFORM
from compose.progress_stream import StreamOutputError
from compose.project import NoSuchService
from compose.project import OneOffFilter
from compose.project import ProjectError
from compose.service import BuildAction
from compose.service import BuildError
from compose.service import ConvergenceStrategy
from compose.service import ImageType
from compose.service import NeedsBuildError
from compose.cli.command import get_config_path_from_options
from compose.cli.command import project_from_options
from compose.cli.docopt_command import DocoptDispatcher
from compose.cli.docopt_command import get_handler
from compose.cli.docopt_command import NoSuchCommand
from compose.cli.errors import UserError
from compose.cli.formatter import ConsoleWarningFormatter
from compose.cli.formatter import Formatter
from compose.cli.log_printer import build_log_presenters
from compose.cli.log_printer import LogPrinter
from compose.cli.utils import get_version_info
from compose.cli.utils import yesno



from pyengine.lib import utils
from pyengine.lib import config
from pyengine.lib.error import *
from pyengine.manager import Manager 


if not IS_WINDOWS_PLATFORM:
    from dockerpty.pty import PseudoTerminal, RunOperation, ExecOperation

log = logging.getLogger(__name__)
console_handler = logging.StreamHandler(sys.stderr)

BASE_DIR = None

def execute_compose(param, base_dir):
    log.debug(os.getcwd())
    command = dispatch(param, base_dir)
    try:
        return command()
    except (KeyboardInterrupt, signals.ShutdownException):
        log.error("Aborting.")
        sys.exit(1)
    except (UserError, NoSuchService, ConfigurationError, ProjectError) as e:
        log.error(e.msg)
        sys.exit(1)
    except BuildError as e:
        log.error("Service '%s' failed to build: %s" % (e.service.name, e.reason))
        sys.exit(1)
    except StreamOutputError as e:
        log.error(e)
        sys.exit(1)
    except NeedsBuildError as e:
        log.error("Service '%s' needs to be built, but --no-build was passed." % e.service.name)
        sys.exit(1)
    except errors.ConnectionError:
        print "Error Son"
        sys.exit(1)


def dispatch(param, base_dir):
    setup_logging()
    dispatcher = DocoptDispatcher(
        TopLevelCommand,
        {'options_first': True, 'version': get_version_info('compose')})
    try:
        options, handler, command_options = dispatcher.parse(param)
    except NoSuchCommand as e:
        commands = "\n".join(parse_doc_section("commands:", getdoc(e.supercommand)))
        log.error("No such command: %s\n\n%s", e.command, commands)
        sys.exit(1)
    log.debug(options)
    setup_console_handler(console_handler, options.get('--verbose'))
    return functools.partial(perform_command, options, handler, command_options, base_dir)


def perform_command(options, handler, command_options, base_dir):
    if options['COMMAND'] in ('help', 'version'):
        # Skip looking up the compose file.
        handler(command_options)
        return

    if options['COMMAND'] == 'config':
        command = TopLevelCommand(None)
        handler(command, options, command_options)
        return

    #project = project_from_options('.', options)
    project = project_from_options(base_dir, options)
    command = TopLevelCommand(project)
    with errors.handle_connection_errors(project.client):
        return handler(command, command_options)


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)

    # Disable requests logging
    logging.getLogger("requests").propagate = False


def setup_console_handler(handler, verbose):
    if handler.stream.isatty():
        format_class = ConsoleWarningFormatter
    else:
        format_class = logging.Formatter

    if verbose:
        handler.setFormatter(format_class('%(name)s.%(funcName)s: %(message)s'))
        handler.setLevel(logging.DEBUG)
    else:
        handler.setFormatter(format_class())
        handler.setLevel(logging.INFO)


# stolen from docopt master
def parse_doc_section(name, source):
    pattern = re.compile('^([^\n]*' + name + '[^\n]*\n?(?:[ \t].*?(?:\n|$))*)',
                         re.IGNORECASE | re.MULTILINE)
    return [s.strip() for s in pattern.findall(source)]


class TopLevelCommand(object):
    """Define and run multi-container applications with Docker.

    Usage:
      docker-compose [-f <arg>...] [options] [COMMAND] [ARGS...]
      docker-compose -h|--help

    Options:
      -f, --file FILE             Specify an alternate compose file (default: docker-compose.yml)
      -p, --project-name NAME     Specify an alternate project name (default: directory name)
      --verbose                   Show more output
      -v, --version               Print version and exit
      -H, --host HOST             Daemon socket to connect to

      --tls                       Use TLS; implied by --tlsverify
      --tlscacert CA_PATH         Trust certs signed only by this CA
      --tlscert CLIENT_CERT_PATH  Path to TLS certificate file
      --tlskey TLS_KEY_PATH       Path to TLS key file
      --tlsverify                 Use TLS and verify the remote
      --skip-hostname-check       Don't check the daemon's hostname against the name specified
                                  in the client certificate (for example if your docker host
                                  is an IP address)

    Commands:
      build              Build or rebuild services
      config             Validate and view the compose file
      create             Create services
      down               Stop and remove containers, networks, images, and volumes
      events             Receive real time events from containers
      exec               Execute a command in a running container
      help               Get help on a command
      kill               Kill containers
      logs               View output from containers
      pause              Pause services
      port               Print the public port for a port binding
      ps                 List containers
      pull               Pulls service images
      restart            Restart services
      rm                 Remove stopped containers
      run                Run a one-off command
      scale              Set number of containers for a service
      start              Start services
      stop               Stop services
      unpause            Unpause services
      up                 Create and start containers
      version            Show the Docker-Compose version information
    """

    def __init__(self, project, project_dir='.'):
        self.project = project
        self.project_dir = '.'

    def build(self, options):
        """
        Build or rebuild services.

        Services are built once and then tagged as `project_service`,
        e.g. `composetest_db`. If you change a service's `Dockerfile` or the
        contents of its build directory, you can run `docker-compose build` to rebuild it.

        Usage: build [options] [SERVICE...]

        Options:
            --force-rm  Always remove intermediate containers.
            --no-cache  Do not use cache when building the image.
            --pull      Always attempt to pull a newer version of the image.
        """
        self.project.build(
            service_names=options['SERVICE'],
            no_cache=bool(options.get('--no-cache', False)),
            pull=bool(options.get('--pull', False)),
            force_rm=bool(options.get('--force-rm', False)))

    def config(self, config_options, options):
        """
        Validate and view the compose file.

        Usage: config [options]

        Options:
            -q, --quiet     Only validate the configuration, don't print
                            anything.
            --services      Print the service names, one per line.

        """
        print "project dir:" + self.project_dir
        environment = Environment.from_env_file(self.project_dir)
        print environment

        config_path = get_config_path_from_options(
            self.project_dir, config_options, environment
        )
        compose_config = config.load(
            config.find(self.project_dir, config_path, environment)
        )

        if options['--quiet']:
            return

        if options['--services']:
            print('\n'.join(service['name'] for service in compose_config.services))
            return

        print(serialize_config(compose_config))

    def create(self, options):
        """
        Creates containers for a service.

        Usage: create [options] [SERVICE...]

        Options:
            --force-recreate       Recreate containers even if their configuration and
                                   image haven't changed. Incompatible with --no-recreate.
            --no-recreate          If containers already exist, don't recreate them.
                                   Incompatible with --force-recreate.
            --no-build             Don't build an image, even if it's missing.
            --build                Build images before creating containers.
        """
        service_names = options['SERVICE']

        self.project.create(
            service_names=service_names,
            strategy=convergence_strategy_from_opts(options),
            do_build=build_action_from_opts(options),
        )

    def down(self, options):
        """
        Stop containers and remove containers, networks, volumes, and images
        created by `up`. Only containers and networks are removed by default.

        Usage: down [options]

        Options:
            --rmi type          Remove images, type may be one of: 'all' to remove
                                all images, or 'local' to remove only images that
                                don't have an custom name set by the `image` field
            -v, --volumes       Remove data volumes
            --remove-orphans    Remove containers for services not defined in
                                the Compose file
        """
        image_type = image_type_from_opt('--rmi', options['--rmi'])
        self.project.down(image_type, options['--volumes'], options['--remove-orphans'])

    def events(self, options):
        """
        Receive real time events from containers.

        Usage: events [options] [SERVICE...]

        Options:
            --json      Output events as a stream of json objects
        """
        def format_event(event):
            attributes = ["%s=%s" % item for item in event['attributes'].items()]
            return ("{time} {type} {action} {id} ({attrs})").format(
                attrs=", ".join(sorted(attributes)),
                **event)

        def json_format_event(event):
            event['time'] = event['time'].isoformat()
            event.pop('container')
            return json.dumps(event)

        for event in self.project.events():
            formatter = json_format_event if options['--json'] else format_event
            print(formatter(event))
            sys.stdout.flush()

    def exec_command(self, options):
        """
        Execute a command in a running container

        Usage: exec [options] SERVICE COMMAND [ARGS...]

        Options:
            -d                Detached mode: Run command in the background.
            --privileged      Give extended privileges to the process.
            --user USER       Run the command as this user.
            -T                Disable pseudo-tty allocation. By default `docker-compose exec`
                              allocates a TTY.
            --index=index     index of the container if there are multiple
                              instances of a service [default: 1]
        """
        index = int(options.get('--index'))
        service = self.project.get_service(options['SERVICE'])
        try:
            container = service.get_container(number=index)
        except ValueError as e:
            raise UserError(str(e))
        command = [options['COMMAND']] + options['ARGS']
        tty = not options["-T"]

        create_exec_options = {
            "privileged": options["--privileged"],
            "user": options["--user"],
            "tty": tty,
            "stdin": tty,
        }

        exec_id = container.create_exec(command, **create_exec_options)
        print exec_id

        if options['-d']:
            print container.start_exec(exec_id, tty=tty)
            print "option -d"
            return

        signals.set_signal_handler_to_shutdown()
        try:
            operation = ExecOperation(
                self.project.client,
                exec_id,
                interactive=tty,
            )
            print "Pseudo Terminal"
            pty = PseudoTerminal(self.project.client, operation)
            pty.start()
        except signals.ShutdownException:
            log.info("received shutdown exception: closing")
        exit_code = self.project.client.exec_inspect(exec_id).get("ExitCode")
        sys.exit(exit_code)

    @classmethod
    def help(cls, options):
        """
        Get help on a command.

        Usage: help [COMMAND]
        """
        if options['COMMAND']:
            subject = get_handler(cls, options['COMMAND'])
        else:
            subject = cls

        print(getdoc(subject))

    def kill(self, options):
        """
        Force stop service containers.

        Usage: kill [options] [SERVICE...]

        Options:
            -s SIGNAL         SIGNAL to send to the container.
                              Default signal is SIGKILL.
        """
        signal = options.get('-s', 'SIGKILL')

        self.project.kill(service_names=options['SERVICE'], signal=signal)

    def logs(self, options):
        """
        View output from containers.

        Usage: logs [options] [SERVICE...]

        Options:
            --no-color          Produce monochrome output.
            -f, --follow        Follow log output.
            -t, --timestamps    Show timestamps.
            --tail="all"        Number of lines to show from the end of the logs
                                for each container.
        """
        containers = self.project.containers(service_names=options['SERVICE'], stopped=True)

        tail = options['--tail']
        if tail is not None:
            if tail.isdigit():
                tail = int(tail)
            elif tail != 'all':
                raise UserError("tail flag must be all or a number")
        log_args = {
            'follow': options['--follow'],
            'tail': tail,
            'timestamps': options['--timestamps']
        }
        print("Attaching to", list_containers(containers))
        log_printer_from_project(
            self.project,
            containers,
            options['--no-color'],
            log_args,
            event_stream=self.project.events(service_names=options['SERVICE'])).run()

    def pause(self, options):
        """
        Pause services.

        Usage: pause [SERVICE...]
        """
        containers = self.project.pause(service_names=options['SERVICE'])
        exit_if(not containers, 'No containers to pause', 1)

    def port(self, options):
        """
        Print the public port for a port binding.

        Usage: port [options] SERVICE PRIVATE_PORT

        Options:
            --protocol=proto  tcp or udp [default: tcp]
            --index=index     index of the container if there are multiple
                              instances of a service [default: 1]
        """
        index = int(options.get('--index'))
        service = self.project.get_service(options['SERVICE'])
        try:
            container = service.get_container(number=index)
        except ValueError as e:
            raise UserError(str(e))
        print(container.get_local_port(
            options['PRIVATE_PORT'],
            protocol=options.get('--protocol') or 'tcp') or '')

    def ps(self, options):
        """
        List containers.

        Usage: ps [options] [SERVICE...]

        Options:
            -q    Only display IDs
        """
        output = {}
        containers = sorted(
            self.project.containers(service_names=options['SERVICE'], stopped=True) +
            self.project.containers(service_names=options['SERVICE'], one_off=OneOffFilter.only),
            key=attrgetter('name'))

        if options['-q']:
            for container in containers:
                print(container.id)
        else:
            headers = [
                'Name',
                'Command',
                'State',
                'Ports',
            ]
            rows = []
            for container in containers:
                command = container.human_readable_command
                if len(command) > 30:
                    command = '%s ...' % command[:26]
                rows.append([
                    container.name,
                    command,
                    container.human_readable_state,
                    container.human_readable_ports,
                ])
                print container.id
                print container.short_id
                print container.labels
                print container.service
                print container.environment

                output[container.name] = [container.human_readable_state, container.human_readable_ports]

            print(Formatter().table(headers, rows))
        return output

    def pull(self, options):
        """
        Pulls images for services.

        Usage: pull [options] [SERVICE...]

        Options:
            --ignore-pull-failures  Pull what it can and ignores images with pull failures.
        """
        self.project.pull(
            service_names=options['SERVICE'],
            ignore_pull_failures=options.get('--ignore-pull-failures')
        )

    def rm(self, options):
        """
        Remove stopped service containers.

        By default, volumes attached to containers will not be removed. You can see all
        volumes with `docker volume ls`.

        Any data which is not in a volume will be lost.

        Usage: rm [options] [SERVICE...]

        Options:
            -f, --force   Don't ask to confirm removal
            -v            Remove volumes associated with containers
            -a, --all     Also remove one-off containers created by
                          docker-compose run
        """
        if options.get('--all'):
            one_off = OneOffFilter.include
        else:
            log.warn(
                'Not including one-off containers created by `docker-compose run`.\n'
                'To include them, use `docker-compose rm --all`.\n'
                'This will be the default behavior in the next version of Compose.\n')
            one_off = OneOffFilter.exclude

        all_containers = self.project.containers(
            service_names=options['SERVICE'], stopped=True, one_off=one_off
        )
        stopped_containers = [c for c in all_containers if not c.is_running]

        if len(stopped_containers) > 0:
            print("Going to remove", list_containers(stopped_containers))
            if options.get('--force') \
                    or yesno("Are you sure? [yN] ", default=False):
                self.project.remove_stopped(
                    service_names=options['SERVICE'],
                    v=options.get('-v', False),
                    one_off=one_off
                )
        else:
            print("No stopped containers")

    def run(self, options):
        """
        Run a one-off command on a service.

        For example:

            $ docker-compose run web python manage.py shell

        By default, linked services will be started, unless they are already
        running. If you do not want to start linked services, use
        `docker-compose run --no-deps SERVICE COMMAND [ARGS...]`.

        Usage: run [options] [-p PORT...] [-e KEY=VAL...] SERVICE [COMMAND] [ARGS...]

        Options:
            -d                    Detached mode: Run container in the background, print
                                  new container name.
            --name NAME           Assign a name to the container
            --entrypoint CMD      Override the entrypoint of the image.
            -e KEY=VAL            Set an environment variable (can be used multiple times)
            -u, --user=""         Run as specified username or uid
            --no-deps             Don't start linked services.
            --rm                  Remove container after run. Ignored in detached mode.
            -p, --publish=[]      Publish a container's port(s) to the host
            --service-ports       Run command with the service's ports enabled and mapped
                                  to the host.
            -T                    Disable pseudo-tty allocation. By default `docker-compose run`
                                  allocates a TTY.
            -w, --workdir=""      Working directory inside the container
        """
        service = self.project.get_service(options['SERVICE'])
        detach = options['-d']

        if IS_WINDOWS_PLATFORM and not detach:
            raise UserError(
                "Interactive mode is not yet supported on Windows.\n"
                "Please pass the -d flag when using `docker-compose run`."
            )

        if options['--publish'] and options['--service-ports']:
            raise UserError(
                'Service port mapping and manual port mapping '
                'can not be used togather'
            )

        if options['COMMAND']:
            command = [options['COMMAND']] + options['ARGS']
        else:
            command = service.options.get('command')

        container_options = build_container_options(options, detach, command)
        exit_code = run_one_off_container(container_options, self.project, service, options)
        output['code'] = exit_code
        return output

    def scale(self, options):
        """
        Set number of containers to run for a service.

        Numbers are specified in the form `service=num` as arguments.
        For example:

            $ docker-compose scale web=2 worker=3

        Usage: scale [options] [SERVICE=NUM...]

        Options:
          -t, --timeout TIMEOUT      Specify a shutdown timeout in seconds.
                                     (default: 10)
        """
        timeout = int(options.get('--timeout') or DEFAULT_TIMEOUT)

        for s in options['SERVICE=NUM']:
            if '=' not in s:
                raise UserError('Arguments to scale should be in the form service=num')
            service_name, num = s.split('=', 1)
            try:
                num = int(num)
            except ValueError:
                raise UserError('Number of containers for service "%s" is not a '
                                'number' % service_name)
            self.project.get_service(service_name).scale(num, timeout=timeout)

    def start(self, options):
        """
        Start existing containers.

        Usage: start [SERVICE...]
        """
        containers = self.project.start(service_names=options['SERVICE'])
        exit_if(not containers, 'No containers to start', 1)

    def stop(self, options):
        """
        Stop running containers without removing them.

        They can be started again with `docker-compose start`.

        Usage: stop [options] [SERVICE...]

        Options:
          -t, --timeout TIMEOUT      Specify a shutdown timeout in seconds.
                                     (default: 10)
        """
        timeout = int(options.get('--timeout') or DEFAULT_TIMEOUT)
        self.project.stop(service_names=options['SERVICE'], timeout=timeout)

    def restart(self, options):
        """
        Restart running containers.

        Usage: restart [options] [SERVICE...]

        Options:
          -t, --timeout TIMEOUT      Specify a shutdown timeout in seconds.
                                     (default: 10)
        """
        timeout = int(options.get('--timeout') or DEFAULT_TIMEOUT)
        containers = self.project.restart(service_names=options['SERVICE'], timeout=timeout)
        exit_if(not containers, 'No containers to restart', 1)

    def unpause(self, options):
        """
        Unpause services.

        Usage: unpause [SERVICE...]
        """
        containers = self.project.unpause(service_names=options['SERVICE'])
        exit_if(not containers, 'No containers to unpause', 1)

    def up(self, options):
        """
        Builds, (re)creates, starts, and attaches to containers for a service.

        Unless they are already running, this command also starts any linked services.

        The `docker-compose up` command aggregates the output of each container. When
        the command exits, all containers are stopped. Running `docker-compose up -d`
        starts the containers in the background and leaves them running.

        If there are existing containers for a service, and the service's configuration
        or image was changed after the container's creation, `docker-compose up` picks
        up the changes by stopping and recreating the containers (preserving mounted
        volumes). To prevent Compose from picking up changes, use the `--no-recreate`
        flag.

        If you want to force Compose to stop and recreate all containers, use the
        `--force-recreate` flag.

        Usage: up [options] [SERVICE...]

        Options:
            -d                         Detached mode: Run containers in the background,
                                       print new container names.
                                       Incompatible with --abort-on-container-exit.
            --no-color                 Produce monochrome output.
            --no-deps                  Don't start linked services.
            --force-recreate           Recreate containers even if their configuration
                                       and image haven't changed.
                                       Incompatible with --no-recreate.
            --no-recreate              If containers already exist, don't recreate them.
                                       Incompatible with --force-recreate.
            --no-build                 Don't build an image, even if it's missing.
            --build                    Build images before starting containers.
            --abort-on-container-exit  Stops all containers if any container was stopped.
                                       Incompatible with -d.
            -t, --timeout TIMEOUT      Use this timeout in seconds for container shutdown
                                       when attached or when containers are already
                                       running. (default: 10)
            --remove-orphans           Remove containers for services not
                                       defined in the Compose file
        """
        start_deps = not options['--no-deps']
        cascade_stop = options['--abort-on-container-exit']
        service_names = options['SERVICE']
        timeout = int(options.get('--timeout') or DEFAULT_TIMEOUT)
        remove_orphans = options['--remove-orphans']
        detached = options.get('-d')

        if detached and cascade_stop:
            raise UserError("--abort-on-container-exit and -d cannot be combined.")

        with up_shutdown_context(self.project, service_names, timeout, detached):
            to_attach = self.project.up(
                service_names=service_names,
                start_deps=start_deps,
                strategy=convergence_strategy_from_opts(options),
                do_build=build_action_from_opts(options),
                timeout=timeout,
                detached=detached,
                remove_orphans=remove_orphans)

            if detached:
                return

            log_printer = log_printer_from_project(
                self.project,
                filter_containers_to_service_names(to_attach, service_names),
                options['--no-color'],
                {'follow': True},
                cascade_stop,
                event_stream=self.project.events(service_names=service_names))
            print("Attaching to", list_containers(log_printer.containers))
            log_printer.run()

            if cascade_stop:
                print("Aborting on container exit...")
                self.project.stop(service_names=service_names, timeout=timeout)

    @classmethod
    def version(cls, options):
        """
        Show version informations

        Usage: version [--short]

        Options:
            --short     Shows only Compose's version number.
        """
        if options['--short']:
            print(__version__)
        else:
            print(get_version_info('full'))


def convergence_strategy_from_opts(options):
    no_recreate = options['--no-recreate']
    force_recreate = options['--force-recreate']
    if force_recreate and no_recreate:
        raise UserError("--force-recreate and --no-recreate cannot be combined.")

    if force_recreate:
        return ConvergenceStrategy.always

    if no_recreate:
        return ConvergenceStrategy.never

    return ConvergenceStrategy.changed


def image_type_from_opt(flag, value):
    if not value:
        return ImageType.none
    try:
        return ImageType[value]
    except KeyError:
        raise UserError("%s flag must be one of: all, local" % flag)


def build_action_from_opts(options):
    if options['--build'] and options['--no-build']:
        raise UserError("--build and --no-build can not be combined.")

    if options['--build']:
        return BuildAction.force

    if options['--no-build']:
        return BuildAction.skip

    return BuildAction.none


def build_container_options(options, detach, command):
    container_options = {
        'command': command,
        'tty': not (detach or options['-T'] or not sys.stdin.isatty()),
        'stdin_open': not detach,
        'detach': detach,
    }

    if options['-e']:
        container_options['environment'] = parse_environment(options['-e'])

    if options['--entrypoint']:
        container_options['entrypoint'] = options.get('--entrypoint')

    if options['--rm']:
        container_options['restart'] = None

    if options['--user']:
        container_options['user'] = options.get('--user')

    if not options['--service-ports']:
        container_options['ports'] = []

    if options['--publish']:
        container_options['ports'] = options.get('--publish')

    if options['--name']:
        container_options['name'] = options['--name']

    if options['--workdir']:
        container_options['working_dir'] = options['--workdir']

    return container_options


def run_one_off_container(container_options, project, service, options):
    if not options['--no-deps']:
        deps = service.get_dependency_names()
        if deps:
            project.up(
                service_names=deps,
                start_deps=True,
                strategy=ConvergenceStrategy.never)

    project.initialize()

    container = service.create_container(
        quiet=True,
        one_off=True,
        **container_options)

    if options['-d']:
        service.start_container(container)
        print(container.name)
        return

    def remove_container(force=False):
        if options['--rm']:
            project.client.remove_container(container.id, force=True)

    signals.set_signal_handler_to_shutdown()
    try:
        try:
            operation = RunOperation(
                project.client,
                container.id,
                interactive=not options['-T'],
                logs=False,
            )
            pty = PseudoTerminal(project.client, operation)
            sockets = pty.sockets()
            service.start_container(container)
            pty.start(sockets)
            exit_code = container.wait()
        except signals.ShutdownException:
            project.client.stop(container.id)
            exit_code = 1
    except signals.ShutdownException:
        project.client.kill(container.id)
        remove_container(force=True)
        sys.exit(2)

    remove_container()
    return sys.exit(exit_code)


def log_printer_from_project(
    project,
    containers,
    monochrome,
    log_args,
    cascade_stop=False,
    event_stream=None,
):
    return LogPrinter(
        containers,
        build_log_presenters(project.service_names, monochrome),
        event_stream or project.events(),
        cascade_stop=cascade_stop,
        log_args=log_args)


def filter_containers_to_service_names(containers, service_names):
    if not service_names:
        return containers

    return [
        container
        for container in containers if container.service in service_names
    ]


@contextlib.contextmanager
def up_shutdown_context(project, service_names, timeout, detached):
    if detached:
        yield
        return

    signals.set_signal_handler_to_shutdown()
    try:
        try:
            yield
        except signals.ShutdownException:
            print("Gracefully stopping... (press Ctrl+C again to force)")
            project.stop(service_names=service_names, timeout=timeout)
    except signals.ShutdownException:
        project.kill(service_names=service_names)
        sys.exit(2)


def list_containers(containers):
    return ", ".join(c.name for c in containers)


def exit_if(condition, message, exit_code):
    if condition:
        log.error(message)
        raise SystemExit(exit_code)


class DockerComposeDriver(Manager):
    GLOBAL_CONF = config.getGlobalConfig()
    def execute(self, template, ):
        """
        Params:
            template: url of template
            env:
            stack_id:
            ctx:
        """
        pass

    def run(self, template, env, stack_id, ctx):
        """
        @params: template
        @params: env
        @params: stack_id
        """
        self.logger.debug("Call run")
        # 1. Load content
        self.env = env
        self.logger.debug("template:%s" % template)
        job = self._loadURI(template)
        self.logger.debug("JOB:\n%s" % job)
        self.ctx = ctx
        self.stack_id = stack_id

        #save as working directory
        prj_path = self._saveTemp(job)

        """
        env
        {'docker-compose':{'ZONE_ID':'xxxx'}}
        """
        # Fetch DOCKER environment from zone and user info
        if env.has_key('docker-compose') == False:
            # TODO: update ERROR msg
            raise ERROR_INVALID_PARAMETER(key='env', value=env)
        my_env = env['docker-compose']
        if my_env.has_key('ZONE_ID') == False:
            # TODO: update ERROR msg
            raise ERROR_INVALID_PARAMETER(key='ZONE_ID', value=my_env)

        zone_id = env['docker-compose']['ZONE_ID']
        cloudMgr = self.locator.getManager('CloudManager')
        docker_info = cloudMgr._getZoneDetail(zone_id)
        
        # USE env as docker-compose environments
        docker_info.update(env['docker-compose'])

        # Get DOCKER_CERT_PATH if possible
        uMgr = self.locator.getManager('UserManager')
        my_cert_path = uMgr.getDockerCertPath(ctx['user_id'])
        if my_cert_path:
            docker_info['DOCKER_CERT_PATH'] = my_cert_path
        else:
            self.logger.info("There are no DOCKER_CERT_PATH for %s" % ctx['user_id'])

        # DOCKER_COMPOSE_TIMEOUT=300
        docker_info['COMPOSE_HTTP_TIMEOUT'] = 1000
        self.logger.debug(docker_info)
        self._updateComposeEnv(prj_path, docker_info)

        # 2. Call Docker-compose up
        os.chdir(prj_path)

        # Before deploy, check current containers (c1)
        cmd = ['ps']
        c1 = execute_compose(cmd, prj_path)

        # docker-compose up -> no return code 
        cmd = ['up','-d']
        execute_compose(cmd, prj_path)

        cmd = ['ps']
        c2 = execute_compose(cmd, prj_path)

        # Update containers from (c2 - c1)
        self.logger.debug(c2)
        self.logger.debug(c1)
        c2_key = set(c2.keys())
        c1_key = set(c1.keys())
        insts = c2_key - c1_key
        self.logger.debug(insts)

        platform =cloudMgr._getZonePlatform(zone_id)
        self.logger.debug("Platform :%s" % platform)
        # if docker-swarm, call DockerDriver
        if platform == "docker":
            pass 
        # if joyent, call JoyentDriver
        elif platform == "joyent":
            for inst in insts:
                self.logger.debug("Register server name=%s" % inst)
                p = {'zone_id': zone_id,
                        'name':inst,
                        'floatingIP':False,
                        'stack_id':stack_id,
                        'register':True,
                        'request':{'name':inst}
                    }
                cloudMgr.registerServer(p, ctx)

        # 3. Update Stack state
        p_mgr = self.locator.getManager('PackageManager')
        p_mgr.updateStackState(stack_id, "running")
   
    def _loadURI(self, uri):
        """
        @param:
            - uri
        @return:
            - content

        load content from uri
        """
        self.logger.debug("_loadURI:%s" % uri)
        r = requests.get(uri)
        self.logger.debug(r.status_code)
        if r.status_code == 200:
            return r.text
        raise ERROR_NOT_FOUND(key='template', value=uri)

    def _saveTemp(self, content):
        """
        @param:
            - content
        @return:
            - saved file path
        """
        # TODO: update working directory
        SAVE_DIR = '/var/www/users/%s/projects' % self.ctx['user_id']
        if not os.path.exists(SAVE_DIR):
            os.mkdir(SAVE_DIR)
            os.chmod(SAVE_DIR, 0700)

        PRJ_PATH = '%s/%s' % (SAVE_DIR, self.stack_id)
        if not os.path.exists(PRJ_PATH):
            os.mkdir(PRJ_PATH)
            os.chmod(PRJ_PATH, 0700)
    
        content_path = "%s/docker-compose.yml" % PRJ_PATH
        fp = open(content_path, 'w')
        fp.write(content)
        fp.close()
        return PRJ_PATH

    def _updateComposeEnv(self, prj_path, info):
        """
        @param: 
            - prj_path: project directory path
            - info: information for environments (dic)
        """
        fp_path = "%s/.env" % prj_path
        self.logger.debug("Create Environment file:%s" % fp_path)
        fp = open(fp_path, 'w')
        for k in info:
            fp.write("%s=%s\n" % (k, info[k]))
        fp.close()

