CHANGES
=======
1.5.0 (2023-07-15)
-------------------
- Added the possibiltity to filter by subject what log on db and not
- Added the column err_msg in order to see from the admin the error messages

1.4.0 (2023-04-06)
------------------

- Added ability to assign callable to `EMAIL_LOG_ATTACHMENTS_PATH`
- Added Django 4.2 support


1.3.0 (2023-02-10)
------------------

- Added Django 4.1 support
- Remove Python 3.6 support
- Add saving of e-mail attachemnts to database
- Add saving of html alternatives to database


1.2.0 (2022-02-08)
------------------

- Set default_auto_field in apps.py (#23)
- Send email even when we can't write the database (#14)
- Fix Django warnings
- Improve CI/pre-commit/formatting (we're using Black now)


1.1.0 (2022-01-27)
------------------

- Added Django 3.2 and 4.0 support
- Dropped Django support for 2.1 and below
- Dropped Python 3.5 support
- Thanks to Alexey Kotenko and Craig Anderson for PRs


1.0.0 (2020-05-19)
------------------

- Added Django 2.x support and Django 3.x support
- Added tests for newer versions of Python 3
- Dropped Django support for 1.10 and below
- Dropped Python 2 support
- Thanks to Mark Jones and Oleg Belousov for attempted PRs

0.2.0 (2014-08-03)
------------------

- Added Django 1.6 and Django 1.7 support.
- Added German and Brazilian Portuguese translations (#3 and #9).  Thanks
  Jannis and Rodrigo Deodoro.
- Fixed email log app name on admin website.
- Output email body in admin interface with linebreaks shown correctly (#6).
  Thanks Keryn Knight.

0.1.0 (2013-05-02)
------------------

Initial release.
