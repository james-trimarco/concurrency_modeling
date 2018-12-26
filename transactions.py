"""
Author: James Trimarco

Data Storage and Retrieval, Homework 9, Question 2

Write a Python program to answer this exercise using Algorithm 20.1. 
Your program should accept any two transactions and output all schedules. 
It should label each serializable schedule with a list of all 
equivalent serial schedules.
"""

import re # for regex matching
from sys import version_info # for checking user's version of Python
import sys 

# Set up global variables and check Python version
read_str = "read_item"
write_str = "write_item"

# Creates boolean value for test that Python major version > 2
py3 = version_info[0] > 2

# Checks python version and prompts for search
if not py3:
    print("Please type 'scl enable rh-python36 bash' to turn on Python 3.")
    sys.exit()

# Define functions
def combine_ordered(l1, l2):
    """
    Takes in two lists. Returns every possible combination of those lists that
    maintains the ordering of both original lists. 
    """
    # Handle cases where one or both lists are empty
    if l1 == [] and l2 == []: return
    if l1 == []: return [l2]
    if l2 == []: return [l1]
    
    # Break lists into front and back
    x, *l1_tail = l1
    y, *l2_tail = l2
    
    # Recurse to generate all legal combinations
    return [ [x] + l for l in combine_ordered(l1_tail, l2) ] + \
           [ [y] + l for l in combine_ordered(l2_tail, l1) ]

def start_program():
    """
    This function provides the user with the option to select default 
    transactions or supply their own. 
    """
    tr1 = "read_item(X); X:= X-N; write_item(X); read_item(Y); Y:= Y+N;write_item(Y)" 
    tr2 = "read_item(X); X:= X + M; write_item(X);"
    while True:
        user_input = input("Would you like to use the default transactions or"
                         "suppy your own? (1 for defaults, 2 for custom)\n").lower()
        
        try:
            user_input = int(user_input)
        except:
            continue
        
        if user_input == 1:
            T_1 = list(filter(None, tr1.split(';'))) 
            T_2 = list(filter(None, tr2.split(';'))) 
            output_all_schedules(T_1, T_2)
            return
        elif user_input == 2:
            T_1 = get_transaction_1()
            T_2 = get_transaction_2()
            output_all_schedules(T_1, T_2)
            return
        elif user_input not in (1, 2):
            continue
            
def get_transaction_1():
    """
    Prompts the reader for transaction one.
    """
    while True:
        input_string = input("Please enter transaction one as a single string "
                             "with semicolons between commands.\n").lower()

        if "read_item" in input_string:
            # split at semicolon
            T_1 = list(filter(None, input_string.split(';')))
            return T_1
        else:
            continue

def get_transaction_2():
    """
    Prompts the reader for transaction two.
    """
    while True:
        input_string = input("Please enter transaction two as a single string "
                             "with semicolons between commands.\n").lower()
        if "read_item" in input_string:
            # split at semicolon
            T_2 = list(filter(None, input_string.split(';'))) 
            return T_2
        else:
            continue

def build_lookup(schedules):
    """
    Runs the logic for determining which graphs are serializable, then 
    builds a simple table of summary information on each schedule to 
    inform output. 
    """
    lib = []
    # create a dictionary of serializabilities
    for idx, schedule in enumerate(schedules):
        lookup = {}
        graph, sch = determine_serial(schedule, idx)
        if graph['T1'] == 'T2' and graph['T2'] == 'T1':
            serializable = "No"
            s_type = 0
        if graph['T1'] == 'T2' and graph['T2'] != 'T1':
            serializable = "Yes"
            s_type = 1
        if graph['T1'] != 'T2' and graph['T2'] == 'T1':
            serializable = "Yes"
            s_type = 2
        lookup = {"idx": idx, 
                  "serializable": serializable, 
                  "s_type": s_type}
        lib.append(lookup)
    return(lib)
    
    
def output_all_schedules(T_1, T_2):
    """
    Creates a list of every possible schedule, calls other functions to
    determine serializability, and prints results to the console. 
    """
    # for printing output
    h_line = '----------------------------------'
    
    # strip whitespaces from input
    for i in range(0, len(T_1)):
        T_1[i] = ("T1:" + T_1[i].strip())
    for i in range(0, len(T_2)):
        T_2[i] = ("T2:" + T_2[i].strip())
        
    # create a list of legal combinations
    schedules = combine_ordered(T_1, T_2)
    
    # create a dictionary of serializability status for all schedules
    lib = build_lookup(schedules)
        
    # For each schedule
    for idx, schedule in enumerate(schedules):
        T1_list = [] # list to store T1 transactions
        T2_list = [] # list to store T2 transactions
        equivalents = [] # list to store nubmers of all equivalent schedules
        
        for entry in lib:
            if entry['idx'] == idx:
                current_data = entry
                
        for entry in lib:
            if entry['s_type'] == current_data['s_type']:
                equivalents.append(entry['idx'])
        
        
        print('\n%s\nSchedule: %s' % (h_line, idx))
        print('%-20s%-20s' % ("Transaction 1", "Transaction 2"))
        print(h_line)
        
        # for each transaction, separate T1s and T2s
        for item in schedule:
            if "T1" in item:
                T1_list.append(item)
                T2_list.append('')
            if "T2" in item:
                T2_list.append(item)
                T1_list.append('')
         
        for i in range(0, len(schedule)):
            print('%-20s%-20s' % (T1_list[i][3:], T2_list[i][3:]))
            

        print(h_line)
        print("Serializable: " + current_data['serializable'])
        
        if current_data['serializable'] == 'Yes':
            print("Equivalents")
            for i in range(0, len(equivalents)):
                if equivalents[i] != current_data['idx']:
                    print(equivalents[i], ', ', end='', sep='')
                if(i != 0 and i % 10 == 0):
                    print("\n", end='', sep='')
        print("\n")
    return
            
    
def create_digraph(schedule):
    """
    This function makes two large passes, one from the point of view of T1, 
    the other from the point of view of T2. 
    
    Within each of these passes, the function loops through the entire schedule,
    checking for conditions that allow it to draw a directed edge.
    """
    graph = {"T1": [],
             "T2": []}
             
    l_1 = ["T1", "T2"]
    for t in l_1: # loop twice, once for each T
        write_token = [] # initialize token for condition 1
        read_token = [] # initialize token for condition 2
        
        if t == "T1": 
            t_not = "T2"
        else: 
            t_not = "T1"
            
        for tr in schedule: 
            
            # Create tokens
            #import pdb; pdb.set_trace()
            if tr['tr'] == t:
                # If T_I has written, create write token
                if write_str in tr['command']:
                    write_token.append(tr['obj'])
                # If T_I has read, create read token
                if read_str in tr['command']:
                    read_token.append(tr['obj'])
            
            # Check against tokens
            if tr['tr'] != t:
                # check for write -> read
                if read_str in tr['command'] and tr['obj'] in write_token:
                    graph[t] = t_not
                # Check for read -> write        
                if write_str in tr['command'] and tr['obj'] in read_token:
                    graph[t] = t_not
                # Check for write -> write
                if write_str in tr['command'] and tr['obj'] in write_token:
                    graph[t] = t_not
    return graph
            

def determine_serial(schedule, idx):
    """
    This function reorganizes the data into a form that allows us to build
    a directed graph from it, and return the output of 'create_digraph()'.
    """
    sch = []
    s = re.compile("(?<=\()(.*?)(?=\))") # find string between parentheses
    for i_idx, item in enumerate(schedule):
        
        if read_str in item or write_str in item:
            obj = s.search(item).group()
            p = {
                    'tr': item[:2],
                    'schedule': idx,
                    'command': item[3:],
                    'order': i_idx + 1,
                    'obj': obj
                    }
            sch.append(p)
    sch = sorted(sch, key=lambda k: k['order'])
    graph = create_digraph(sch)
    return(graph, sch)
        

start_program()