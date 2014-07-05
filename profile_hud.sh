#!/bin/sh

python -m cProfile -o hudprofile.txt HUD.py
runsnake hudprofile.txt

