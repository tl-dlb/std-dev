#! /bin/bash

chmod -R ugo+rw ../

find ./ -type f -name "*.sh" -exec chmod ug+x {} \+

