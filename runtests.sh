#!/bin/sh
coverage erase
tox
coverage html --omit='email_log/migrations/*'
