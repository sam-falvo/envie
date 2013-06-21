#!/bin/bash
#
# This script wraps a bare git checkout into its own Go project workspace.
# It does this through symbolic link magic.
# src/.../pkgname -> .

# Configuration
PKGBASE=github.com/sam-falvo
PKGNAME=envie

# Get canonical directory name of build script, and change to that directory,
# so we always know where we are.
CWD=$(dirname $0)
CWD=$(cd $CWD; pwd)
echo $0
exit

# Establish Go project environment.
export GOPATH=$(pwd)
mkdir -p src/$PKGBASE
ln -s $(pwd) src/$PKGBASE/$PKGNAME

# Follow and install dependencies.
# I think this will need to be a simple python script or something.
python envie-deps.py

# Remind user to set GOPATH.
echo "Reminder -- environment variables set in this program do not"
echo "propegate to your interactive shell session.  You'll want to"
echo "execute the following command if you haven't set the GOPATH"
echo "variable already:"
echo ""
echo "export GOPATH=$GOPATH"

