=================
python-anyconfig
=================

.. image:: https://api.travis-ci.org/ssato/python-anyconfig.png?branch=master
   :target: https://travis-ci.org/ssato/python-anyconfig
   :alt: Test status

.. image:: https://pypip.in/version/anyconfig/badge.svg
   :target: https://pypi.python.org/pypi/anyconfig/
   :alt: Latest Version

.. image:: https://pypip.in/py_versions/anyconfig/badge.svg
   :target: https://pypi.python.org/pypi/anyconfig/
   :alt: Supported Python versions

.. image:: https://coveralls.io/repos/ssato/python-anyconfig/badge.png
   :target: https://coveralls.io/r/ssato/python-anyconfig
   :alt: Coverage Status

.. image:: https://landscape.io/github/ssato/python-anyconfig/master/landscape.png
   :target: https://landscape.io/github/ssato/python-anyconfig/master
   :alt: Code Health

This is a python library called 'anyconfig' [#]_  provides generic access to
configuration files in any formats (to be in the future) with configuration
merge / cascade / overlay support.

* Author: Satoru SATOH <ssato@redhat.com>
* License: MIT

Current supported configuration file formats are:

* JSON w/ json or simplejson
* YAML w/ PyYAML
* Ini w/ configparser
* XML w/ lxml or ElementTree (experimental)
* Other formats some pluggale backends support (see the next sub section)

.. [#] This name took an example from the 'anydbm' library in python dist,

Other anyconfig backend modules
---------------------------------

Anyconfig utilizes plugin mechanism provided by setuptools [#]_ and 
I wrote a few backend plugin modules as references:

* Java properties file w/ pyjavaproperties [#]_ (experimental):

  * https://github.com/ssato/python-anyconfig-pyjavaproperties-backend

* Ini file like format which configobj [#]_ supports (experimental):

  * https://github.com/ssato/python-anyconfig-configobj-backend

.. [#] http://peak.telecommunity.com/DevCenter/setuptools#dynamic-discovery-of-services-and-plugins
.. [#] https://pypi.python.org/pypi/pyjavaproperties
.. [#] https://pypi.python.org/pypi/configobj

Usage
======

see also: output of `python -c "import anyconfig; help(anyconfig)"`

anyconfig module
-------------------

To load single config file::

  import anyconfig

  # Config type (format) is automatically detected by filename (file
  # extension).
  data1 = anyconfig.load("/path/to/foo/conf.d/a.yml")

  # Loaded config data is a dict-like object.
  # examples:
  # data1["a"] => 1
  # data1["b"]["b1"] => "xyz"
  # data1["c"]["c1"]["c13"] => [1, 2, 3]

  # Same as above
  data2 = anyconfig.single_load("/path/to/foo/conf.d/a.yml")

  # Or you can specify config type explicitly.
  data3 = anyconfig.load("/path/to/foo/conf.d/b.conf", "yaml")

  # Same as above
  data4 = anyconfig.single_load("/path/to/foo/conf.d/b.conf", "yaml")

Also, you can pass backend (config loader) specific optional parameters to
these load and dump functions::

  # from python -c "import json; help(json.load)":
  # Help on function load in module json:
  #
  # load(fp, encoding=None, cls=None, object_hook=None, parse_float=None, parse_int=None, parse_constant=None, object_pairs_hook=None, **kw)
  #    Deserialize ``fp`` (a ``.read()``-supporting file-like object containing
  #    a JSON document) to a Python object.
  #    ...
  data5 = anyconfig.load("foo.json", parse_float=None)

.. note::

   The returned object is an instance of anyconfig.mergeabledict.MergeableDict
   class by default, to support recursive merge operations needed when loading
   multiple config files.

To load multiple config files::

  import anyconfig

  # Specify config files by list of paths:
  data1 = anyconfig.load(["/etc/foo.d/a.json", "/etc/foo.d/b.json"])

  # Similar to the above but all or one of config files are missing:
  data2 = anyconfig.load(["/etc/foo.d/a.json", "/etc/foo.d/b.json"],
                         ignore_missing=True)

  # Specify config files by glob path pattern:
  data3 = anyconfig.load("/etc/foo.d/*.json")

  # Similar to the above, but parameters in the former config file will be simply
  # overwritten by the later ones:
  data4 = anyconfig.load("/etc/foo.d/*.json", merge=anyconfig.MS_REPLACE)

On loading multiple config files, you can choose 'strategy' to merge
configurations from the followings:

* anyconfig.MS_REPLACE: Replace all configuration parameter values provided in
  former config files are simply replaced w/ the ones in later config files.

  For example, if a.yml and b.yml are like followings:

  a.yml::

    a: 1
    b:
       - c: 0
       - c: 2
    d:
       e: "aaa"
       f: 3

  b.yml::

    b:
       - c: 3
    d:
       e: "bbb"

  then::

    load(["a.yml", "b.yml"], merge=anyconfig.MS_REPLACE)

  will give object such like::

    {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb"}}

* anyconfig.MS_NO_REPLACE: Do not replace configuration parameter values
  provided in former config files.

  For example, if a.yml and b.yml are like followings:

  a.yml::

    b:
       - c: 0
       - c: 2
    d:
       e: "aaa"
       f: 3

  b.yml::

    a: 1
    b:
       - c: 3
    d:
       e: "bbb"

  then::

    load(["a.yml", "b.yml"], merge=anyconfig.MS_NO_REPLACE)

  will give object such like::

    {'a': 1, 'b': [{'c': 0}, {'c': 2}], 'd': {'e': "bbb", 'f': 3}}

* anyconfig.MS_DICTS: Merge dicts recursively. That is, the following::

    load(["a.yml", "b.yml"], merge=anyconfig.MS_DICTS)

  will give object such like::

    {'a': 1, 'b': [{'c': 3}], 'd': {'e': "bbb", 'f': 3}}

* anyconfig.MS_DICTS_AND_LISTS: Merge dicts and lists recursively. That is, the
  following::

    load(["a.yml", "b.yml"], merge=anyconfig.MS_DICTS_AND_LISTS)

  will give object such like::

    {'a': 1, 'b': [{'c': 0}, {'c': 2}, {'c': 3}], 'd': {'e': "bbb", 'f': 3}}


CLI frontend
-------------

There is a CLI frontend 'anyconfig_cli' to demonstrate the power of this library.

It can process various config files and output a merged config file::

  ssato@localhost% anyconfig_cli -h
  Usage: anyconfig_cli [Options...] CONF_PATH_OR_PATTERN_0 [CONF_PATH_OR_PATTERN_1 ..]

  Examples:
    anyconfig_cli --list
    anyconfig_cli -I yaml -O yaml /etc/xyz/conf.d/a.conf
    anyconfig_cli -I yaml '/etc/xyz/conf.d/*.conf' -o xyz.conf --otype json
    anyconfig_cli '/etc/xyz/conf.d/*.json' -o xyz.yml \
      --atype json -A '{"obsoletes": "sysdata", "conflicts": "sysdata-old"}'
    anyconfig_cli '/etc/xyz/conf.d/*.json' -o xyz.yml \
      -A obsoletes:sysdata;conflicts:sysdata-old
    anyconfig_cli /etc/foo.json /etc/foo/conf.d/x.json /etc/foo/conf.d/y.json
    anyconfig_cli '/etc/foo.d/*.json' -M noreplace
    anyconfig_cli '/etc/foo.d/*.json' --get a.b.c
    anyconfig_cli '/etc/foo.d/*.json' --set a.b.c=1

  Options:
    --version             show program's version number and exit
    -h, --help            show this help message and exit
    -L, --list            List supported config types
    -o OUTPUT, --output=OUTPUT
                          Output file path
    -I ITYPE, --itype=ITYPE
                          Select type of Input config files from ini, json, xml,
                          yaml [Automatically detected by file ext]
    -O OTYPE, --otype=OTYPE
                          Select type of Output config files from ini, json,
                          xml, yaml [Automatically detected by file ext]
    -M MERGE, --merge=MERGE
                          Select strategy to merge multiple configs from
                          replace, noreplace, merge_dicts, merge_dicts_and_lists
                          [merge_dicts]
    -A ARGS, --args=ARGS  Argument configs to override
    --atype=ATYPE         Explicitly select type of argument to provide configs
                          from ini, json, xml, yaml.  If this option is not set,
                          original parser is used: 'K:V' will become {K: V},
                          'K:V_0,V_1,..' will become {K: [V_0, V_1, ...]}, and
                          'K_0:V_0;K_1:V_1' will become {K_0: V_0, K_1: V_1}
                          (where the tyep of K is str, type of V is one of Int,
                          str, etc.
    --get=GET             Specify key path to get part of config, for example, '
                          --get a.b.c' to config {'a': {'b': {'c': 0, 'd': 1}}}
                          gives 0 and '--get a.b' to the same config gives {'c':
                          0, 'd': 1}.
    --set=SET             Specify key path to set (update) part of config, for
                          example, '--set a.b.c=1' to a config {'a': {'b': {'c':
                          0, 'd': 1}}} gives {'a': {'b': {'c': 1, 'd': 1}}}.
    -x, --ignore-missing  Ignore missing input files
    -s, --silent          Silent or quiet mode
    -q, --quiet           Same as --silent option
    -v, --verbose         Verbose mode
  ssato@localhost%

Build & Install
================

If you're Fedora or Red Hat Enterprise Linux user, you can install experimental
RPMs on http://copr.fedoraproject.org/coprs/ from:

* http://copr.fedoraproject.org/coprs/ssato/python-anyconfig/

or if you want to build yourself, then try::

  $ python setup.py srpm && mock dist/SRPMS/python-anyconfig-<ver_dist>.src.rpm
  
or::

  $ python setup.py rpm

and install built RPMs. 

Otherwise, try usual ways to build and/or install python modules such like 'pip
install anyconfig', 'easy_install anyconfig' and 'python setup.py bdist', etc.

How to hack
==============

How to write backend plugin modules
-------------------------------------

Backend class must inherit anyconfig.backend.ConfigParser and need some member
variables and method ('load_impl' and 'dumps_impl' at minimum) implementations.

JSON and YAML backend modules (anyconfig.backend.{json,yaml}_) should be good
examples to write backend modules, I think.

Also, please take a look at some example backend plugin modules mentioned in
the `Other anyconfig backend modules`_ section.

How to test
-------------

Try to run './aux/runtest.sh [path_to_python_code]'.

TODO
======

* Make configuration (file) backends pluggable: Done

  * Remove some backends to support the following configuration formats:
  
    * Java properties file: Done
    * XML ?

* Allow users to select other containers for the tree of configuration objects
* Establish the way to test external backend modules

.. vim:sw=2:ts=2:et:
