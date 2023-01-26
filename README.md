# KoGekko
KoGekko is a simple Python utility to retrieve html pages and ran some analises on them.

KoGekko is designed to be a library providing the functionalities for data retrieval plus
a CLI for interaction. This allows the user of the library to use it through other means,
if necessary (e.g. testing, custom GUI)

## Libraries Used

- [loguru][3]: Simplified logging system
- [lxml][4]: XML parsing engine for `requests-html`
- [platformdirs][5]: OS abstraction layer for user folder paths retrieval
- [pywebcopy][6]: Library to demonstrate the possible future operation for local dump of web-page assets
- [requests][7]: The classic network requests library
- [requests-html][8]: Specialized version of `requests` written by the same team

## Usage instructions

The application can be used directly by installing the dependencies provided in the file `Pipfile` and
then call the application directly:

```shell
    $ python src/main.py -h
```

However it's recommended to use a `venv` manager to avoid polluting your system with extraneous dependencies,
e.g. [pipenv][9]:

```shell
    $ pipenv install
    $ pipenv run python src/main.py -h
```

Additionally the application is shipped with a Docker compose definition, allowing the user to run it
without installing anything on the host machine. For this a launcher script has been provided in order to
simplify the user experience:

```shell
    $ ./ko_gekko.sh -h
```

The image uses two permanent volumes to keep logs and the database of last timestamp of website fetch, plus
one bind for runtime data sharing between container and host.

The image can be built using standard `docker-compose` calls:

```shell
    $ docker compose build
```

The application expects a list of space-separated URLs to retrieve, allowing also to pipe the request through
`stdin`. Additional options are also provided:

- `h` - Print help
- `o` - Custom download path
- `m` - Metadata (i.e. last fetch timestamp, link amount and image amount for each requested URL)
- `v` - Verbose output
- `l` - Interface call to `pywebcopy` to show the potential effect of a fully-local copy of a page

## Future work

- Add unit tests for the application
- Implement the local page download as it would require some extra HTML attributes rewrite to be sure that
    assets are loaded from the correct paths
- Possibly test [Podman][1] as container engine instead of Docker under Linux in order to fix the permission
    issues related to rootless/isolation containerization

## Known issues

If using [user namespace isolation][2] with Docker under Linux it is possible that the temporary directory used
to store the retrieved pages before being copied to the local folder cannot be deleted due to the difference
between the calling user and the temporary user used by Docker to run the isolated container. While this is an
issue with constantly running operating systems it should not be in a standar use case as all the temporary
folders are provided by the os and are deleted at shutdown/reboot.

The output flag `o` is handled directly by the Python application, meaning that it will have undesired effects
when passed to the runner script since it will change the output path inside the container, potentially losing
all results unless a volume is mounted on the target container path

[1]: https://podman.io/
[2]: https://docs.docker.com/engine/security/userns-remap/
[3]: https://github.com/Delgan/loguru
[4]: https://lxml.de/
[5]: https://github.com/platformdirs/platformdirs
[6]: https://github.com/rajatomar788/pywebcopy/
[7]: https://github.com/psf/requests
[8]: https://github.com/psf/requests-html
[9]: https://github.com/pypa/pipenv
