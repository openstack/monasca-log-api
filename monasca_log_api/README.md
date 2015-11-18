# Monasca-log-api Python

## Installation

To install the python api implementation, git clone the source and run the
following command::
```sh
    sudo python setup.py install
```

If it installs successfully, you will need to make changes to the following
two files to reflect your system settings, especially where kafka server is
located::

```sh
    /etc/monasca/log-api-config.conf
    /etc/monasca/log-api-config.ini
```

Once the configurations are modified to match your environment, you can start
up the server by following the following instructions.

To start the server, run the following command:

Running the server in foreground mode
```sh
    gunicorn -k eventlet --worker-connections=2000 --backlog=1000
             --paste /etc/monasca/log-api.ini
```

Running the server as daemons
```sh
    gunicorn -k eventlet --worker-connections=2000 --backlog=1000
             --paste /etc/monasca/log-api.ini -D
```

## Testing

### PEP8 guidelines
To check if the code follows python coding style, run the following command
from the root directory of this project:

```sh
    tox -e pep8
```

### Testing
To run all the unit test cases, run the following command from the root
directory of this project:

```sh
    tox -e py27   (or -e py26, -e py33)
```

### Coverage
To generate coverage results, run the following command from the root
directory of this project:

```sh
    tox -e cover
```

### Building

To build an installable package, run the following command from the root
directory of this project:

```sh
  python setup.py sdist
```

### Documentation

To generate documentation, run the following command from the root
directory of this project:

```sh
make html
```

That will create documentation under build folder relative to root of the
project.
