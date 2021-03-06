
F/NLF Backend
=======================

A REST backend for F/NLF's applications built on [Eve](http://python-eve.org)

* [Eve]

Getting Started
---------------

### Requirements
* Python 3.3+
* [Virtualenv] \(optional but highly recommended\)
* Mongodb > 3 (and a running instance)
* 

Download or clone the repository
```
git clone https://github.com/fnlf/fnlf-backend.git
```
Then use virtualenv
```
virtualenv fnlf-backend
cd fnlf-backend
source bin/activate
```

Note: Make sure you are using a supported python version, most likely your system has multiple python versions installed. To specify version:
```
virtualenv -p /usr/bin/python3.3 fnlf-backend
```

### Install
```
pip install -r requirements.txt
```

**Note:** No database nor any Melwin integration is supplied here since this contains private information. To download visit [F/NLF Wiki](https://doc.nlf.no/confluence/display/NLFAVVIK/Development+files) You will need access to the developer pages for this project.

Restore latest database dump (production)
```
mongorestore --drop -d fnlf dump/fnlf
```

scf.py needs to be moved to `ext/scf.py`

### Starting Eve

Optionally configure `settings.py` to suit your environment but the default should be fine

`python run.py`

The REST api is now available on http://localhost:8080/api/v1

Note: Issues describe some common issues with the 3rd party modules

You should also install the frontend.

Issues
------
Eve is currently running 0.7-dev branch

Frontend
--------

The frontend/client is located at [fnlf-client]

Features
--------

This project utilizes the power and flexibility of Eve and Flask, the following ...

* Automatic versioning
* ....


Usage
-----

See http://localhost:8080/api/v1/docs for the autogenerated documentation of the api

Use cUrl, Postman for Chrome or the Eve client to test the api 

Issues
------

Discovered a bug? Please create an issue here on GitHub!

https://github.com/fnlf/fnlf-backend/issues

Versioning
----------

For transparency and insight into our release cycle, releases will be numbered with the follow format:

`<major>.<minor>.<patch>`

And constructed with the following guidelines:

* Breaking backwards compatibility bumps the major
* New additions without breaking backwards compatibility bumps the minor
* Bug fixes and misc changes bump the patch

For more information on semantic versioning, please visit http://semver.org/.

Testing
-------

Tests are written using Eve Mocker. To run the tests run `python tests.py` with a running instance of the REST api

Developers
----------

If you plan on contributing to this project, be sure to read the [contributing guidelines][contributing-guidelines].

*These contributing guidelines were proudly stolen from the 
[Flight](https://github.com/flightjs/flight) project*

Looking to contribute something? Here's how you can help.

Bug Reports
------------

A bug is a _demonstrable problem_ that is caused by the code in the
repository. Good bug reports are extremely helpful – thank you!

Guidelines for bug reports:

1. **Use the GitHub issue search** &mdash; check if the issue has already been
   reported.

2. **Check if the issue has been fixed** &mdash; try to reproduce it using the
   latest `master` or integration branch in the repository.

3. **Isolate the problem** &mdash; ideally create a reduced test
   case and a live example.

4. Please try to be as detailed as possible in your report. Include specific
   information about the environment – operating system and version, browser
   and version, version of fnlf-backend – and steps required to reproduce the 
  issue.

Feature Requests & Contribution Enquiries
-----------------------------------------

Feature requests are welcome. But take a moment to find out whether your idea
fits with the scope and aims of the project. It's up to *you* to make a strong
case for the inclusion of your feature. Please provide as much detail and
context as possible.

Contribution enquiries should take place before any significant pull request,
otherwise you risk spending a lot of time working on something that we might
have good reasons for rejecting.

Pull Requests
-------------

Good pull requests – patches, improvements, new features – are a fantastic
help. They should remain focused in scope and avoid containing unrelated
commits.

Make sure to adhere to the coding conventions used throughout the codebase
(indentation, accurate comments, etc.) and any other requirements (such as test
coverage).

Please follow this process; it's the best way to get your work included in the
project:

1. [Fork](http://help.github.com/fork-a-repo/) the project, clone your fork,
   and configure the remotes:
   
   **Note:** You should clone this into a virtualenv directory

   ```bash
   # Clone your fork of the repo into the current directory
   git clone https://github.com/<your-username>/fnlf-backend
   # Navigate to the newly cloned directory
   cd <repo-name>
   # Assign the original repo to a remote called "upstream"
   git remote add upstream git://github.com/fnlf/fnlf-backend
   ```

2. If you cloned a while ago, get the latest changes from upstream:

   ```bash
   git checkout master
   git pull upstream master
   ```

3. Install the dependencies , and create a new topic branch (off the main project development
   branch) to contain your feature, change, or fix:

   ```bash
   pip install requirements.txt
   git checkout -b <topic-branch-name>
   ```

4. Make sure to update, or add to the tests when appropriate. Patches and
   features will not be accepted without tests. Run `python tests.py` to check that
   all tests pass after you've made changes.

5. Commit your changes in logical chunks. Provide clear and explanatory commit
   messages. Use Git's [interactive rebase](https://help.github.com/articles/interactive-rebase) feature to tidy up
   your commits before making them public.

6. Locally merge (or rebase) the upstream development branch into your topic branch:

   ```bash
   git pull [--rebase] upstream master
   ```

7. Push your topic branch up to your fork:

   ```bash
   git push origin <topic-branch-name>
   ```

8. [Open a Pull Request](https://help.github.com/articles/using-pull-requests/)
    with a clear title and description.

9. If you are asked to amend your changes before they can be merged in, please
   use `git commit --amend` (or rebasing for multi-commit Pull Requests) and
   force push to your remote feature branch. You may also be asked to squash
   commits.


Authors
-------

* **Einar Huseby** ([GitHub](https://github.com/ehu))
* **Håkon Søgnen** ([GitHub](https://github.com/haakon-sognen))

Contributors
------------

Thanks for assistance and contributions:

* Your name

License
-------

Copyright [F/NLF].

Licensed under the MIT License

[fnlf-client]: https://github.com/fnlf/fnlf-client
[fnlf-backend]: https://github.com/fnlf/fnlf-backend
[F/NLF Wiki]: https://nlf-az-db02.cloudapp.net/confluence
[F/NLF]: http://www.nlf.no/fallskjerm

<!-- assets -->
[zipball]: http://fnlf.github.com/fnlf-backend/releases/latest/fnlf-backend.zip

<!-- github links -->
[contributing-guidelines]: https://github.com/fnlf/fnlf-backend/blob/master/CONTRIBUTING.md
[contributors]: https://github.com/fnlf/fnlf-backend/contributors
[issues]: https://github.com/fnlf/fnlf-backend/issues

<!-- deep links -->


<!-- links to third party projects -->
[Eve]: https://github.com/nicolaiarocci/eve
[Eve-docs]: https://github.com/nicolaiarocci/eve-swagger
[Eve-Mocker]: https://github.com/tsileo/eve-mocker
[Virtualenv]: http://virtualenv.readthedocs.org/en/latest/
