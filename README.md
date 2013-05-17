Probabilistic Graphical Models
==============================

This package can be used to create graphical models and perform various operations on them.

Usage
-----

python -m pgm.main [-h] [-e EVIDENCE] [-u HEURISTIC] [-v VARS [VARS ...]] [-t]model function


positional arguments:
  model                 the model file for your network
  function              the function to perform on your network. Current
                        choices: joint_distribution, variable_elimination,
                        partition_function

optional arguments:
  -h, --help            show this help message and exit
  -e EVIDENCE, --evidence EVIDENCE
                        an evidence file to condition on
  -u HEURISTIC, --heuristic HEURISTIC
                        the heuristic to be used when performing variable
                        elimination. If not specified, variables will be
                        simply be eliminated in the order they were given
  -v VARS [VARS ...], --vars VARS [VARS ...]
                        The list of variables for variable eliminationor MAP
                        inference
  -t, --time            Set this to get timing stats at runtinme
