#!/bin/bash
RESTORE='\033[0m'
RED='\033[00;31m'
GREEN='\033[00;32m'

function success {
    echo -ne "$1"
    len=$${#1}
    gap=$$((20-$$len))
    i=0
    while [ $$i -le $$gap ]
    do
       echo -ne " "
       i=$$(( $$i + 1 ))
    done
    echo -e " [ \033[00;32mOK\033[0m ]"
}

function failure {
    echo -ne "$1"
    len=$${#1}
    gap=$$((15-$$len))
    i=0
    while [ $$i -le $$gap ]
    do
       echo -ne " "
       i=$$(( $$i + 1 ))
    done
    echo -e " [ $${RED}FAILURE$${RESTORE} ]"
    echo "$${@:2}"
}

log=$$(${options['run']}) && success "${options['title']}" || failure "${options['title']}" "$$log"
