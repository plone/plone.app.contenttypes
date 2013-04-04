#!/bin/bash

for f in `find $1 -not -name __init__.py -name "*.py" -exec grep -H -E -o -c "coding: utf-8" {} \; | grep 0 | cut -d":" -f1`;
do
    echo '# -*- coding: utf-8 -*-' > ${f}.tmp.bla
    cat ${f} >> ${f}.tmp.bla
    mv ${f}.tmp.bla ${f}
done

