###########
jwtlib
###########

.. readme_inclusion_marker


Dev setup
~~~~~~~~~

Initialize local repository
---------------------------

.. code-block:: bash

    $ pipenv install -d                     # Install all dependencies
    $ pipenv run python setup.py develop    # Setup the pkg for local development
    $ pipenv shell                          # Open shell within the virtualenv


Available commands
------------------

.. code-block:: bash

    $ peltak --help     # Show the list of available commands
    $ peltak test       # Run tests
    $ peltak lint       # Run code checks
    $ peltak docs       # Build documentation using Sphinx
