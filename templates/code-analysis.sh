#!/bin/bash
RESTORE='\033[0m'
RED='\033[00;31m'
GREEN='\033[00;32m'

function success {
    echo -ne $1
    echo -e " [ \033[00;32mOK\033[0m ]"
}

function failure {
    echo -ne $1
    echo -e " [ $${RED}FAILURE$${RESTORE} ]"
    echo "$${@:2}"
}

log=$$(${options['bin']} ${options['directory']}) && success ${options['title']} || failure ${options['title']} $$log
