#!/bin/sh

##==============================================================================
## Simple genkernel command to fully install kernel from the current
## directory. This is useful when manually configuring and building
## kernel, but still wanting to use some genkernel features.
##
## Just run this from /usr/src/linux -- you'll find everything
## installed in your /boot/
##
## This is the better version, that should do pretty much everything..
## Unluckily, we cannot interleave comments in commands.. :(
##==============================================================================

#genkernel \
#    # If we already built this kernel
#    --no-clean \
#    # If we already configured this kernel
#    --no-mrproper \
#    # If we didn't configure the kernel yet
#    --oldconfig \
#    # This is the default..
#    --kernel-config=.config \
#    # We want to configure grub
#    --bootloader=grub \
#    # We want the splash screen
#    --splash \
#    # Install after building
#    --install \
#    # Be verbose!
#    --loglevel=5 \
#    # Where is the kernel dir?
#    --kerneldir=. \
#    # Standard MAKEOPTS
#    --makeopts='-j5' \
#    # Yeah, build everything!
#    all


genkernel \
    --no-clean \
    --no-mrproper \
    --oldconfig \
    --kernel-config=.config \
    --bootloader=grub \
    --splash \
    --install \
    --loglevel=5 \
    --kerneldir=. \
    --makeopts='-j5' \
    all
