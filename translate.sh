#!/bin/bash
# http://blog.brendel.com/2010/09/how-to-customize-djangos-default.html
echo "### Entering project"
cd bubula2
echo "### Translating all messages..."
django-admin.py makemessages -a
echo "### Removing commented-out manual messages..."
find locale -name 'django.po' -exec sed s/^\#\~\ // -i {} \;
echo "### Compiling messages..."
django-admin.py compilemessages
echo "### Done!"
