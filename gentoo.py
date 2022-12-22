import json
import subprocess
class Drive:
    def __init__(self, drive):
        self.drive = drive

    def mount_boot_drive(self):
        if 'boot' in self.drive:
            subprocess.call(['mount', self.drive['boot'], '/boot'])
    def mount_drive(self, partition, location):
        subprocess.call(['mount', partition, location])

class Users:
    def __init__(self,users):
        self.users = users
        for user in self.users:
            print(user)
            self.init_user(user)
    def init_user(self, user):
        if 'name' in user:
            print('Name detected.')
            if 'passwd' in user:
                print('Passwd detected.')
                if 'groups' in user:
                    print('Groups detected.')
#                    subprocess.call(['useradd', '-m', user['name'], '-p', user['passwd'], '-G', ','.join(user['groups'])])
#                    print(['useradd', '-m', user['name'], '-p', user['passwd'], '-G', ','.join(user['groups'])])

                else:
#                    subprocess.call(['useradd', '-m', user['name'], '-p', user['passwd']])
                    print(['useradd', '-m', user['name'], '-p', user['passwd']])

            else:
#                subprocess.call(['useradd', '-m', user['name']])
                print((['useradd', '-m', user['name']]))

        else:
            exit(1)
    

class Config:
    def __init__(self, config):
        self.config = config
        self.conf = self.init_config()
    def init_config(self) -> dict:
        def init_drive():
            if 'drive' in self.config:
                return Drive(self.config['drive'])
        def init_user():
            if 'users' in self.config:
                return Users(self.config['users'])
        return dict([
            ('users', init_user()),
            ('drive', init_drive())
            ])

def run_cmd(cmd):
    subprocess.call(cmd)

def eselect(opt: str):
    run_cmd(['eselect', opt, 'list'])
    ropt = input('Choose option: ')
    run_cmd(['eselect', opt, 'set', ropt])

class Emerge:
    def __init__(self) -> None:
        self.init()
    def init(self):
        run_cmd(['emerge-webrsync'])
        run_cmd(['emerge', '--sync', '--quiet'])
        eselect('profile')
    def world(self):
        run_cmd(['emerge', '--ask', '--verbose', '--update', '--deep', '--newuse', '@world'])
def load_config() -> Config:
    with open('config.json') as f:
        return Config(json.load(f))

x = load_config()
v = x.conf['drive']
v.mount_boot_drive()
