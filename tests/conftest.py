import os
import sys

# Loads persistence.py itself, whatever folder the repository is cloned into, e.g. a bot's submodule folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
