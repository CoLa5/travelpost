"""Writer Tests."""

import pathlib

PATH: pathlib.Path = pathlib.Path(__file__).parent
DATA_PATH: pathlib.Path = PATH / "data"
OUT_PATH: pathlib.Path = PATH / "out"
IMG_PATH: pathlib.Path = DATA_PATH / "condor_123456.jpg"
IMG_COVER_PATH: pathlib.Path = DATA_PATH / "berlin.jpg"
MAP_PATH: pathlib.Path = DATA_PATH / "map.jpg"
TXT_PATH: pathlib.Path = DATA_PATH / "o_henry_the_gift_of_the_magi.txt"
