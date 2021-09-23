import os
import json
from ftplib import FTP, error_perm

# projectDir = os.getcwd()
with open('xua-plugin-settings.json') as f:
    config = json.loads(f.read())

hostname = config['deploy']['ftp']['hostname']
port = config['deploy']['ftp']['port']
username = config['deploy']['ftp']['username']
password = config['deploy']['ftp']['password']
source = config['deploy']['source']
destination = config['deploy']['destination']

ftp = FTP()
ftp.connect(hostname, port)
ftp.login(username, password)


def placeFiles(path):
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        serverpath = os.path.join(destination, name)

        if os.path.isfile(localpath):
            print("STOR", serverpath, localpath)
            ftp.storbinary('STOR ' + serverpath, open(localpath, 'rb'))
        elif os.path.isdir(localpath):
            print("MKD", serverpath)
            try:
                ftp.mkd(serverpath)
            except error_perm as e:
                # ignore "directory already exists"
                if not e.args[0].startswith('550'):
                    raise
            print("CWD", serverpath)
            ftp.cwd(serverpath)
            placeFiles(localpath)
            print("CWD", "..")
            ftp.cwd("..")


placeFiles(source)
ftp.quit()
