#!/bin/bash
RESTORE='\033[0m'
RED='\033[00;31m'
GREEN='\033[00;32m'

title="${options['title']}"

function check {
    command -v ${options.get('check', '')} >/dev/null 2>&1 || {
        echo -ne $$title
        #echo >&2 "${options.get('check', '')} not installed!";
        len=$${#title}
        gap=$$((18-$$len))
        i=0
        while [ $$i -le $$gap ]
        do
           echo -ne " "
           i=$$(( $$i + 1 ))
        done
        echo -e " [ \033[00;33mSKIP\033[0m ]"
        exit 1;
    }
}

function success {
    echo -ne $$title
    len=$${#title}
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
    echo -ne $$title
    len=$${#title}
    gap=$$((15-$$len))
    i=0
    while [ $$i -le $$gap ]
    do
       echo -ne " "
       i=$$(( $$i + 1 ))
    done
    echo -e " [ $${RED}FAILURE$${RESTORE} ]"
    echo "$${@:1}"
}

check
log=$$(${options['run']}) && success || failure "$$log"
