#!/bin/sh
coverage erase
tox
coverage html --omit='email_log/tests/*,email_log/migrations/*'
