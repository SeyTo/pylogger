import argparse
import configparser
import os
import subprocess
import datetime


CONFIG_FILE = 'configs'
NOTIFIER_FILE = 'notifier.sh'
TASK_DURATION = 30
DAEMON_SH = 'daemon.sh'

def notify(header, message, sound):
    # os.execl(NOTIFIER_FILE, header, message, sound)
    subprocess.call(['./notifier.sh', header, message, sound])


def get_all_projects():
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    return parser.items('projects')


def get_current_project():
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    name = parser.get('lastproject', 'name')
    try:
        return { 'name': name, 'loc': parser.get('projects', name) }
    except configparser.InterpolationError:
        print('No project {0} found. Please select a new project.'.format(name))
        return None


def start_daemon(hrs, min):
    # user should start atd
    # subprocess.call(['sudo', 'atd'])
    time = '{0:0>2}:{1:0>2}'.format(hrs,min)
    subprocess.call(['at', time, '-f', DAEMON_SH])


def set_current_project(project):

    CURRENT_PROJECT = project
    parser = configparser.RawConfigParser()
    parser.read(CONFIG_FILE)
    with open(CONFIG_FILE, 'w') as config_file:
        parser.set('lastproject', 'name', project[0])
        parser.write(config_file)


def parse_configs(header, key):
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read('configs')
    return parser.get(header, key)


def log(head, log):
    pass


def checkProcessRunning(program):
    import psutil
    return program in (p.name() for p in psutil.process_iter())


def printCurrentTime():
    now = datetime.datetime.now()
    return "{0}:{1}".format(now.hour, now.minute)


class SetTimeout(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if not checkProcessRunning('atd'):
            print('atd not running. Please sudo run atd program.')
            return
        now = datetime.datetime.now()
        val = int(values[0]) + now.minute
        hours = int(val / 60) + now.hour
        min = (val % 60)
        start_daemon(hours , min)


class DoProject(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        if values == 'v':
            self.show(values)
        elif values == 'r':
            self.resume()
        elif values == 'p':
            self.pause()
        elif values == 's':
            self.stop()

    def list_all_sub_dirs(path=''):
        root = parse_configs('directories','root')
        print(root)
        for subdirs in os.listdir(root):
            print(subdirs)

    def show(self, values):
        # shows all the projects and the current project 
        print( '{0:15}     {1}'.format('Name', 'Location'))
        print( 55 * '-')
        projects = get_all_projects()
        for proj in projects:
            print("{0:15} --> {1} ".format(proj[0], proj[1]))
        print( 55 * '-')
        print("Current Project: {0} ".format(CURRENT_PROJECT['name']))
        chosen = input("Choose Project: ")
        found = False
        for proj in projects:
            if chosen == proj[0]:
                set_current_project(proj)
                print ('Current Project Selected is ' + chosen)
                found = True
        if not found:
            try:
                a = int(chosen)
                if a > len(projects) or a < 1:
                    raise ValueError
                else:
                    set_current_project(projects[int(chosen) - 1])
            except ValueError:
                print('Cant understand what you mean! Nothing will change.')

    def resume(self):
        # resumes the current project if it has been stopped or paused
        # todo: resume the timer
        # start atd
        # put at using timeout to call this script wth timeout call
        # todo: log project is resuming
        notify('Resuming {0} project'.format(CURRENT_PROJECT['name']), printCurrentTime(), 'resume')
        # log 
        print('resume')

    def pause(self):
        # pauses the current project timer if it had been resumed
        notify('Pausing {0} project'.format(CURRENT_PROJECT['name']), printCurrentTime(), 'pause')
        # log 
        print('pause')
        # cancel daemon -> get remaining time -> wait 

    def stop(self):
        # stops the current project timer if it had been resumed
        notify('Stopping {0}'.format(CURRENT_PROJECT['name']), printCurrentTime(), 'stopping')
        # log 
        print('stopped')


class LogForProject(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        if not values: return 
        if not CURRENT_PROJECT:
            print('No current project specified. Specify a project first.')
        str = ' '.join(values)
        print('LogForProject: ' + ' '.join(values))


class SetLogLevel(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        LOG_LEVEL = values[0]
        print(LOG_LEVEL)


# select a current project or none
CURRENT_PROJECT = get_current_project()
if not CURRENT_PROJECT:
    CURRENT_PROJECT['name'] = 'No Current Project Selected'

# 0=stopped, 1=started, 2=paused, 3=timeout
CURRENT_STATE = 0
LOG_LEVEL = 0

parser = argparse.ArgumentParser(prog='Logger', description='Log your activities')
# options to show, resume, pause, stop the current project
parser.add_argument('-c', choices=['v', 'r', 'p', 's'], action=DoProject, help='v - show/select projects\n r - resume project\n p - pause project\n s - stop project (done for the day, doing another project)')
parser.add_argument('-t', nargs=1, action=SetTimeout, help='set timout for the project.')
parser.add_argument('-l', nargs=1, action=SetLogLevel, help='set log level.')
parser.add_argument('LOG', nargs='*', action=LogForProject, help='log some information on the project')
parser.parse_args();

