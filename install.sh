#!/bin/bash

#################################################################################
# Coding conventions
#
# - Prefer portability, but don't sacrifice security and whitespace awareness
#   to it.
#
# - Prefer builtins over external commands.
#
# - But, use fast external commands to process very large inputs.
#
# - Avoid unnecessary subshells and pipelines.
#
# - Don't preoptimize.
#
# - Learn the rules of quoting. Then, use quotes.
#
# - Use functions to improve readability and control scope.
# 
# - Don't give scripts silly file extensions.
#
# - Never change directory without checking that it worked.
#
# - Eschew hobgoblins
#
#
# "A foolish consistency is the hobgoblin of little minds, adored by little
#  statesmen and philosophers and divines."
#
#  . Ralph Waldo Emerson
#
#
################################################################################

# install tensorflow
export TF_BINARY_URL=https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow-0.11.0rc0-cp27-none-linux_x86_64.whl
pip install --ignore-installed --upgrade $TF_BINARY_URL

# install scp connection support
conda install paramiko
pip install scp

# give tensorflow ipython support
conda install ipython
