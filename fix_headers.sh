#!/bin/bash
HEADER_FILE="header.gpl"
EOL="#EOL"

for sf in `find . -iname "*.py" \! -regex "\./openid/.*"`; do
        if grep ${EOL} ${sf} > /dev/null; then
                echo "${sf}: got header"
        else
                echo -n "${sf}: adding header..."
                mv ${sf} ${sf}.noheader
                cat ${HEADER_FILE} ${sf}.noheader > ${sf}
                rm ${sf}.noheader
                echo "done"
        fi
done
