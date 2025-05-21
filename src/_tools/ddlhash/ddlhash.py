from __future__ import print_function

import re
import sys
import hashlib

ddl_file = open(sys.argv[1], 'rb').read()
file_str = ddl_file.decode('utf-8')
file_str = '\n'.join(file_str.splitlines())
a = re.compile(r'CREATE\s+TABLE\s+schema_version.*Revision;', re.S | re.I).split(file_str)
h = (hashlib.sha1(a[-1].encode('utf-8')).hexdigest() if len(a) > 1 else '')
new_content = re.sub(r'\"\$Revision:\s*[a-z:A-Z0-9]*\s*\$\"', u'"$Revision: ' + h + u'$"', file_str) + '\n'

new_file = open(sys.argv[1] + '.new', 'wb')
new_file.write(new_content.encode('utf-8'))
