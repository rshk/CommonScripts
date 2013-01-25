#!/bin/bash

## Simple genkernel command to fully install kernel from the current
## directory. This is useful when manually configuring and building
## kernel, but still wanting to use some genkernel features.
##
## Just run this from /usr/src/linux -- you'll find everything
## installed in your /boot/

#genkernel --no-clean --no-mrproper --kernel-config=.config --install all


## This is the better version, that should do pretty much everythin
genkernel \
    --no-clean \ # If we already built this kernel
    --no-mrproper \ # If we already configured this kernel
    --oldconfig \ # If we didn't configure the kernel yet
    --kernel-config=.config \ # This is the default..
    --bootloader=grub \ # We want to configure grub
    --splash \ # We want the splash screen
    --install \ # Install after building
    --loglevel=5 \ # Be verbose!
    --kerneldir=. \ # Where is the kernel dir?
    --makeopts='-j5' \ # Standard MAKEOPTS
    all # Yeah, build everything!
