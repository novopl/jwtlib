###########
jwtlib
###########

.. readme_inclusion_marker


Dev setup
~~~~~~~~~

Initialize local repository
---------------------------

.. code-block:: bash

    $ poetry install
    $ poetry shell                          # Open shell within the virtualenv


Available commands
------------------

.. code-block:: bash

    $ peltak --help     # Show the list of available commands
    $ peltak test       # Run tests
    $ peltak check      # Run code checks
    $ peltak docs       # Build documentation using Sphinx


Release new version
-------------------

While on master branch, you can release the current state of it by running

.. code-block:: bash

    peltak release create               # Create a patch release
    peltak release create -t patch      # Create a patch release
    peltak release create -t minor      # Create a minor release
    peltak release create -t major      # Create a major release
