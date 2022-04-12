from ctypes import *
import chess
import chess.polyglot
import random
import os

nnue = cdll.LoadLibrary("./nnue/libnnueprobe.exe")
nnue.nnue_init(b"nnue/networks/nn-vdv.nnue")
