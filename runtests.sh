#!/bin/sh
coverage erase
tox
coverage html --include='email_log/*' --omit='email_log/tests/*'
