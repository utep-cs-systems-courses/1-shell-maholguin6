#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, re

stdin  = 0
stdout = 1
stderr = 2

###############################################################################
"""
this section is in charge of processing strings to accomodate different
 operator signs such | or < >.
 """
 
def peek_stack(stack):
    
    if stack:
        return stack[-1]    # this will get the last element of stack
    else:
        return None
    
    
def operator_redirect_write_1(l):
    args_r_1 = []
    args_r_2 = []
    l_a = l.split()
    prog = list(reversed(l_a))
    while peek_stack(prog) != None:
        if peek_stack(prog) != '>':
            args_r_2.append(prog.pop())
        
        if peek_stack(prog) == '>':
            args_r_1 = args_r_2.copy()
            args_r_2.clear()
            prog.pop()
            
        if peek_stack(prog) == None:
            return args_r_1, args_r_2
        

def operator_redirect_read_1(l):
    args_l_1 = []
    args_l_2 = []
    l_a = l.split()
    prog = list(reversed(l_a))
    while peek_stack(prog) != None:
        if peek_stack(prog) != '<':
            args_l_2.append(prog.pop())
        
        if peek_stack(prog) == '<':
            args_l_1 = args_l_2.copy()
            args_l_2.clear()
            prog.pop()
            
        if peek_stack(prog) == None:
            return args_l_1, args_l_2


def operator_a(l):
    args_a = []
    l_a = l.split()
    prog = list(reversed(l_a))
    while prog:
        args_a.append(prog.pop())
        paint(args_a)
    return args_a
    
    
def operator_pipe_1(l):
    args_p_1 = []; args_p_2 = []
    l_a = l.split()
    prog = list(reversed(l_a))
    while peek_stack(prog) != None:
        if peek_stack(prog) != '|':
            args_p_2.append(prog.pop())
        
        if peek_stack(prog) == '|':
            args_p_1 = args_p_2.copy()
            args_p_2.clear()
            prog.pop()
            
        if peek_stack(prog) == None:
            return args_p_1, args_p_2


def operator_pipe_2(l):
    args1 = []; args2 = []; args3 = []
    index = 0
    l_a = l.split()
    prog = list(reversed(l_a))
    while peek_stack(prog) != None:
        if peek_stack(prog) != '|':
            args3.append(prog.pop())
        
        if peek_stack(prog) == '|' and index == 0:
            args2 = args3.copy()
            args3.clear()
            prog.pop()
            index += 1
            
        if peek_stack(prog) == '|' and index == 1:
            args1 = args2.copy()
            args2 = args3.copy()
            args3.clear()
            prog.pop()
            index +=1
                  
        if peek_stack(prog) == None:
            return args1, args2, args3
        

###############################################################################


def paint(string, fd=1, end='\n'):
    """
    print out string 
    """
    os.write(fd, (f'{string}{end}').encode())

    
def ch_dir(folder=''):
    """
    Change directory based on arguments 
    """  
    try:
        if folder == '':
            os.chdir(os.environ['HOME'])
        else:
            os.chdir(folder)
    except FileNotFoundError:
        paint(f'file {folder} not found')
        
        
def l_2(a,b,c):
    """
    process two pipe

    Parameters
    ----------
    a : List
        list of commands and args for first child.
    b : List
        List of commands and args for second child.
    c : List
        List of commands and args for third child.
    Returns
    -------
    None.

    """
    
    pr_one,pw_one = os.pipe()        
    rc_one = os.fork()     
                    
    if rc_one < 0:
        
        sys.exit(1)
        
    elif rc_one == 0:
        
        os.dup2(pw_one, stdout, True)
        perform_task(a)
        
        
    elif rc_one > 0:

        pr_two, pw_two = os.pipe()

        rc_two = os.fork()            
        
        if rc_two < 0:
            sys.exit(1)
        elif rc_two == 0:
            
            os.dup2(pr_one, stdin, True)
            os.dup2(pw_two, stdout, True)
            perform_task(b)
        
        elif rc_two > 0:
            
            rc_three = os.fork()
            
            if rc_three < 0:
                sys.exit(1)
            elif rc_three == 0:
                
                os.dup2(pr_two, stdin, True)
                perform_task(c)
                
            else:
                os.wait()
                sys.exit(0)
        else:
            os.wait()
            sys.exit(0)
    else:
        os.wait()
    
    
def l_1(a,b):
    """
    process one pipe

    Parameters
    ----------
    a : List
        list of commands and args for first child.
    b : List
        List of commands and args for second child.

    Returns
    -------
    None.

    """
    pr,pw = os.pipe()        #create file decriptosrs for the pipe connection
    rc = os.fork()                          # fork a new Procces

    if rc < 0:

        sys.exit(1)

    elif rc == 0:                   #  child - will write to pipe
        os.dup2(pw, stdout, True)
        perform_task(a)
                
    elif rc > 0:
    
        rcc = os.fork()             # fork another children in between children and parent
        
        if rcc < 0:
            sys.exit(1)
        elif rcc == 0:
            os.dup2(pr,stdin,True)
            perform_task(b)
            
            sys.exit(1)
        else:
            os.wait()
            sys.exit(0)
    else:
        os.wait()
    

def r_w(a,b):
    rc = os.fork()                          # fork a new Procces

    if rc < 0:

        sys.exit(1)

    elif rc == 0:                   #  child - will write to pipe
        to_write(b)
        perform_task(a)
        
        sys.exit(1)
    
    else:
        os.wait()


def r_r(a,b):
    rc = os.fork()                          # fork a new Procces

    if rc < 0:

        sys.exit(1)

    elif rc == 0:                   #  child - will write to pipe
        to_read(b)
        perform_task(a)
        
        sys.exit(1)
    else:
        os.wait()


def l_0(a):
    rc = os.fork()                          # fork a new Procces

    if rc < 0:

        sys.exit(1)

    elif rc == 0:                   #  child - will write to pipe
        try:
            if len(a) == 0:
                pass
            else:
                perform_task(a)
        except OSError:
            paint('Command not found.')
    else:
        os.wait()

    
def to_write(a):
        os.close(stdout)                 # redirect child's stdout
        try:
            os.open(a[0], os.O_CREAT | os.O_WRONLY);
            os.set_inheritable(stdout, True)
        except TypeError:
            paint("Ups... something went wrong try again.")
    
def to_read(a):
        os.close(stdin)                 # redirect child's stdin
        try:
            os.open(a[0], os.O_RDONLY);
            os.set_inheritable(stdin, True)
        except TypeError:
            paint("Ups... something went wrong try again.")
    
    
def perform_task(a):
            
    for dir in re.split(":", os.environ['PATH']):
        program = "%s/%s" % (dir, a[0])
        try:
           os.execve(program, a, os.environ)
        except FileNotFoundError:
            pass

def cursor():
    if "PS1" not in os.environ:
        cursor = os.getcwd()
        paint(cursor + f': {n} :=>', end='')
    else:
        cursor = os.environ['PS1']
        
    user_input = os.read(stdin, 100).decode()
    possible_command = user_input[0:-1]
    return possible_command
    
###############################################################################

def cd(folder):
    """
    Change directory based on arguments 
    """  
    if len(j) == 1:
        try:
            os.chdir(os.environ['HOME'])
        except FileNotFoundError:
            os.write(1, (f'file {folder} not found\n').encode())
    else:
        try:
            os.chdir(j[1])
        except FileNotFoundError:
            os.write(1, (f'file {folder} not found\n').encode())

###############################################################################

n = 1
while 1:
    i = cursor()
    if len(re.findall('\|', i))  == 2:
        a,b,c = operator_pipe_2(i)
        l_2(a,b,c)
    elif len(re.findall('\|', i))  == 1:
        d,e = operator_pipe_1(i)
        l_1(d,e)
    elif len(re.findall('>', i)) == 1:
        f,g = operator_redirect_write_1(i)
        r_w(f,g)
    elif len(re.findall('<', i)) == 1:
        h,i = operator_redirect_read_1(i)
        r_r(h,i)
    elif 'cd' in i:
        j = operator_a(i)
        cd(j)
        
    elif 'exit' in i:
        sys.exit(0)
        
    else:
        z = operator_a(i)
        l_0(z)
       
    n += 1
