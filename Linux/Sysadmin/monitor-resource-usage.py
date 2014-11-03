#!/bin/bash

from __future__ import print_function, division

import sys
import time

import psutil


command = sys.argv[1:]
proc = psutil.Popen(command)

max_mem = (0,) * 20
total_mem = (0,) * 20
iterations = 0


while True:
    if (not proc.is_running()) or (proc.status() == psutil.STATUS_ZOMBIE):
        proc.wait()
        print("Process terminated with code: {0}".format(proc.returncode))
        break

    mem = proc.memory_info_ex()
    max_mem = mem.__class__(*(max(x, y) for x, y in zip(max_mem, mem)))
    total_mem = mem.__class__(*(x + y for x, y in zip(total_mem, mem)))

    iterations += 1

    time.sleep(1)


avg_mem = total_mem.__class__(*(x / iterations for x in total_mem))


print("-" * 70)
print("Resource usage statistics\n")
print("    Maximum memory usage\n")
for key, val in zip(total_mem.__class__._fields, total_mem):
    print("        {0}: {1}".format(key, val))
