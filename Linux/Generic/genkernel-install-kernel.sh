#!/bin/sh

## Simple genkernel command to fully install kernel from the current
## directory. This is useful when manually configuring and building
## kernel, but still wanting to use some genkernel features.
##
## Just run this from /usr/src/linux -- you'll find everything
## installed in your /boot/

genkernel --no-clean --no-mrproper --kernel-config=.config --install all
