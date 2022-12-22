import json
import subprocess
def run_cmd(cmd):
    subprocess.call(cmd)
def write_file(file, str):
    with open(file, 'w') as f:
        f.write(str)
    f.close()
def append_file(file, str):
    with open(file, 'a') as f:
        f.write('\n')
        f.write(str)
    f.close()

def eselect(opt: str):
    run_cmd(['eselect', opt, 'list'])
    ropt = input('Choose option: ')
    run_cmd(['eselect', opt, 'set', ropt])

def concat_str(strs):
    tmp = ''
    for str in strs:
        tmp += str
    return tmp

class Drive:
    def __init__(self, drive):
        self.drive = drive

    def mount_boot_drive(self):
        if 'boot' in self.drive:
            subprocess.call(['mount', self.drive['boot'], '/boot'])
    def mount_drive(self, partition, location):
        subprocess.call(['mount', partition, location])
    def set_fstab(self):
        if 'fs' in self.drive:
            write_file('/etc/fstab', concat_str([self.drive['boot'] , '  ' , '/boot' , '   ' , self.drive['fs'] , '    ' , 'defaults' , '    ' , '0 2']))
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
                    subprocess.call(['useradd', '-m', user['name'], '-p', user['passwd'], '-G', ','.join(user['groups'])])
                    print(['useradd', '-m', user['name'], '-p', user['passwd'], '-G', ','.join(user['groups'])])

                else:
                    subprocess.call(['useradd', '-m', user['name'], '-p', user['passwd']])
                    print(['useradd', '-m', user['name'], '-p', user['passwd']])

            else:
                subprocess.call(['useradd', '-m', user['name']])
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
        def portage():
            if 'portage' in self.config:
                return Portage(self.config['portage'])
        return dict([
            ('users', init_user()),
            ('drive', init_drive()),
            ('portage', portage())
            ])

    def generic(self):
        if 'timezone' in self.config:
            write_file('/etc/timezone', self.config['timezone'])
        if 'init-system' in self.config:
            if self.config['init-system'] == 'openrc':
                run_cmd(['emerge', '--config', 'sys-libs/timezone-data'])
            elif self.config['init-system'] == 'systemd':
                run_cmd(['ln -sf ../usr/share/zoneinfo/' ++ self.config['timezone'], '/etc/localtime'])
        if 'locale' in self.config:
            write_file('/etc/locale.gen', self.config['locale'])
            run_cmd(['locale-gen'])
            eselect('locale')           
            run_cmd(['env-update'])
        run_cmd(['emerge', '--ask', 'sys-kernel/linux-firmware'])
class Portage:
    def __init__(self, config) -> None:
        self.config = config
        pass
    def init(self):
        run_cmd(['emerge-webrsync'])
        run_cmd(['emerge', '--sync', '--quiet'])
        eselect('profile')
    def world(self):
        self.init()
        run_cmd(['emerge', '--ask', '--verbose', '--update', '--deep', '--newuse', '@world'])
    def install_pkg(self, pkg):
        run_cmd(['emerge', '--ask', pkg])
    def set_use_flags(self):
        with open('/etc/portage/make.conf', 'a') as f:
            if 'use-flags' in self.config:
                f.write('\n')
                f.write('USE="{}"'.format(' '.join(self.config['use-flags'])))
                f.write('\n')
                f.write('ACCEPT_LICENSE="-* @FREE @BINARY-REDISTRIBUTABLE"')
        f.close()
    def install_kernel(self):
        eselect('kernel')
        self.install_pkg('sys-kernel/genkernel')
    def genkernel(self):
        run_cmd(['genkernel', 'all'])
def load_config() -> Config:
    with open('config.json') as f:
        return Config(json.load(f))

x = load_config()
v = x.conf['drive']
v.mount_boot_drive()
emerge = x.config['portage']
emerge.set_use_flags()
x.generic()
emerge.install_kernel()
v.set_fstab()
emerge.genkernel()
