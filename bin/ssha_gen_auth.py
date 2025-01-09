import codecs
import os
import stat
import sys
import optparse
from base64 import urlsafe_b64encode

try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1

def get_ssha_encoded_string(password):
    """Encode the given `string` using "Secure" SHA.

    Taken from zope.password.password but we cannot depend on that package.
    """
    encoder = codecs.getencoder('utf-8')
    _hash = sha1(encoder(password)[0])
    salt = os.urandom(4)
    _hash.update(salt)
    return b'{SSHA}' + urlsafe_b64encode(_hash.digest() + salt)


def main():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '-u', '--user', dest="username",  default=None, help=("Provide a user name for the master account"))    
    parser.add_option(
        '-p', '--password', dest="password",  default=None, help=("Provide a password for the master account"))
    parser.add_option(
        '-s', '--site_name', dest="sitename",  default='sample', help=("Provide a Site Name for this site"))
    
    options, args = parser.parse_args()
    if options.username is None or options.password is None:
        parser.print_help()
        return 1

    password = get_ssha_encoded_string(options.password).decode()
    
    pwfile = '/opt/gserver/var/.gpasswd.cfg'
    with open(pwfile, "w") as f:
        f.write('[site_zcml]\n')
        f.write(f'username = "{options.username}"\n')
        f.write(f'password = "{password}"\n')
        f.write(f'sitename = "{options.sitename}"\n')
    os.chmod(pwfile, stat.S_IRUSR | stat.S_IWUSR)
    
    print(f"Site configuration details updated in {pwfile}")

if __name__ == "__main__":
    main()
