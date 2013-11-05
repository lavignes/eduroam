#!/usr/bin/env python
# Linux eduroam setup script
import ConfigParser
import uuid
import os
import getpass

ini = ConfigParser.ConfigParser()
networks = os.listdir('certs')

if os.geteuid() is not 0:
  exit('Please run this as root.')

addr = raw_input('Enter institution network (eg. csuchico.edu): ')

if addr not in networks:
  exit('Network \'%s\' was not found.' % addr)

print '%s found...' % addr

if not os.path.exists(os.path.join('/', 'etc',
  'NetworkManager', 'system-connections')):
  exit('Network Manager does not seem to be installed.')

uid = uuid.uuid4()
pemfile = os.path.join('/', 'etc',
  'NetworkManager', 'system-connections', '%s-ca-cert.pem' % uid)

eduroamfile = os.path.join('/', 'etc',
  'NetworkManager', 'system-connections', 'eduroam')

# Copy key
keybuffer = open(os.path.join('certs', addr)).read()
with open(pemfile, 'w') as f:
  f.write(keybuffer)
os.chmod(pemfile, 0600)
print 'Copied key: %s...' % pemfile

username = raw_input('Enter institution username: ')
password = getpass.getpass('Enter institution password: ')

ini.add_section('connection')
ini.set('connection', 'id', 'eduroam')
ini.set('connection', 'uuid', uid)
ini.set('connection', 'type', '802-11-wireless')

ini.add_section('802-11-wireless')
ini.set('802-11-wireless', 'ssid', 'eduroam')
ini.set('802-11-wireless', 'mode', 'infrastructure')
ini.set('802-11-wireless', 'security', '802-11-wireless-security')

ini.add_section('802-1x')
ini.set('802-1x', 'eap', 'ttls;')
ini.set('802-1x', 'identity', username)
ini.set('802-1x', 'anonymous-identity', 'anonymous@%s' % addr)
ini.set('802-1x', 'ca-cert', pemfile)
ini.set('802-1x', 'phase2-auth', 'pap')
ini.set('802-1x', 'password', password)

ini.add_section('802-11-wireless-security')
ini.set('802-11-wireless-security', 'key-mgmt', 'wpa-eap')

with open(eduroamfile, 'w') as f:
    ini.write(f)
os.chmod(eduroamfile, 0600)

print 'All done! :-)'
