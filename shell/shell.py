#! /usr/bin/env python3


import os, sys, re



def parametrize(string):
    args = []
    for i in string.split():
        args.append(i)
 
    return args


def param(str):
    """
    Separates atring of comands and arguments into a 
    list of strings
    """

    commands = []
    for item in str.split():
        commands.append(item)

    return commands


def ch_dir(folder):
    """
    Change directory based on arguments 
    """  
    try:
        os.chdir(folder)
    except FileNotFoundError:
        os.write(1, (f'file {folder} not found\n').encode())



def fail():
    """
    reports fork could not be completed
    """

    os.write(1,(f'fork failed {os.getpid()}\n').encode())
    sys.exit(1)


def perform_task(commands):
    """
    use a  procces to perform commands
    """
    for dir in re.split(':', os.environ['PATH']):
        program = f'{dir}/{commands[0]}'
        try:
            os.execve(program, commands, os.environ)
        except OSError:
            pass #os.write(1,(f'Error code: {error}\n').encode())


def execute_command(commands):
    """
    Create a child process with fork and execute the command
    """
    rc = os.fork()

    if rc < 0:
        fail()
    elif rc == 0:
        perform_task(commands)
    else:
        os.wait()

def redirect(commands):
    """
    Redirect stdout to a file
    """
    rc = os.fork()                  # invoking a child

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        args = [commands[0], commands[1]]

        os.close(1)                 # redirect child's stdout
        os.open(commands[3], os.O_CREAT | os.O_WRONLY);
        os.set_inheritable(1, True)

        perform_task(args)

    else:                           # parent (forked ok)
        os.wait()

    
def main():
    """
    run my shell forever or at leas until 
    user type in exit
    """

    while 1:
        os.write(1, (f'{os.getcwd()} $').encode())
        args = parametrize(os.read(0, 32).decode())
        if (args[0] == 'exit'):
            sys.exit(0)
        elif (args[0] == 'help'):
            os.write(1, ('sorry no help at this time').encode())
        elif((args[0] == 'cd'):
            ch_dir(args[1])
        elif( args[0] == 'cd'):
            os.chdir(os.environ['HOME'])
        else:
            if (len(args) > 3 and args[1] == '>'):
                redirect(args)
                
        execute_command(args)


main()
