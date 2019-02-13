CHANGES
=======

1.0.0 (2019-02-13)
------------------

- Added Django 2.x support
- Remove Django < 1.11 support (older version will work for them)
- Fixed security vulnerability if email contained any text created by the user.
- Added a template to display the email to prevent the vulnerability
- Tox testing and Travis CI updated for new versions of Django and Python

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
