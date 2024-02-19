#!/bin/bash

LOG_DIR="/var/www/flaskapp/servicelogs"
LOG_NAMES=("a1111" "Fooocus" "kohya")

for LOG_NAME in "${LOG_NAMES[@]}"; do
    OLD_LOG="${LOG_DIR}/${LOG_NAME}.old.txt"

        rm -f "${OLD_LOG}"

        if [ -f "${LOG_DIR}/${LOG_NAME}.txt" ]; then
        mv "${LOG_DIR}/${LOG_NAME}.txt" "${OLD_LOG}"
    fi

    touch "${LOG_DIR}/${LOG_NAME}.txt"

    chown flaskroot:flaskroot "${LOG_DIR}/${LOG_NAME}.txt"
    chmod 640 "${LOG_DIR}/${LOG_NAME}.txt"
done

