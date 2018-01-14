import argparse
import configparser
import os


CONFIG_FILE = 'configs'


def get_all_projects():
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    return parser.items('projects')


def get_current_project():
    parser = configparser.ConfigParser()
    parser.read(CONFIG_FILE)
    name = parser.get('lastproject', 'name')
    try:
        return parser.get('projects', name)
    except configparser.InterpolationError:
        print('No project {0} found. Please select a new project.'.format(name))
        return None


def parse_configs(header, key):
    parser = configparser.ConfigParser(allow_no_value=True)
    parser.read('configs')
    return parser.get(header, key)


class SetTimeout(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        print(values)


class DoProject(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, const=None, default=None, type=None, choices=None, required=False, help=None, metavar=None):
        super().__init__(option_strings, dest, nargs, const, default, type, choices, required, help, metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        if values == 'v':
            self.show()
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

    def show(self):
        # shows all the projects and the current project 
        print( '{0:15}     {1}'.format('Name', 'Location'))
        print( 55 * '-')
        for proj in get_all_projects():
            print("{0:15} --> {1} ".format(proj[0], proj[1]))
        print( 55 * '-')
        print("Current Project: {0} ".format(CURRENT_PROJECT))
         
    def resume(self):
        # resumes the current project if it has been stopped or paused
        # todo: resume the timer
        # todo: log project is resuming
        
        print('resume')

    def pause(self):
        # pauses the current project timer if it had been resumed
        print('pause')

    def stop(self):
        # stops the current project timer if it had been resumed
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
    CURRENT_PROJECT = 'No Current Project Selected'

# 0=stopped, 1=started, 2=paused, 3=timeout
CURRENT_STATE = 0
LOG_LEVEL = 0

parser = argparse.ArgumentParser(prog='Logger', description='Log your activities')
# options to show, resume, pause, stop the current project
parser.add_argument('-c', choices=['v', 'r', 'p', 's'], action=DoProject)
parser.add_argument('-t', nargs=1, action=SetTimeout, type=int, help='set timout for the project.')
parser.add_argument('-l', nargs=1, action=SetLogLevel, help='set log level.')
parser.add_argument('LOG', nargs='*', action=LogForProject, help='log some information on the project')
parser.parse_args();
