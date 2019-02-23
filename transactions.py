"""
Author: James Trimarco

When we have two schedules of reads and writes — let's call them transactions 
T_1 and T_2 — we can lose information if reads and writes don't take place in a 
certain order. For example, T_1 might read and modify file X, then T_2 reads 
and modifies the same file, but then T_1 saves its modifications. So T_2's 
changes are lost. 

The following program finds all combinations of two schedules and provides 
information on which ones are safe. It takes two schedules as input in
the following format:

    "read_item(X); 
    X:= X-N; 
    write_item(X); 
    read_item(Y); 
    Y:= Y+N;
    write_item(Y)"

The output includes every possible schedule resulting from their combination, 
along with information on whether the schedule is _serializable_ or not. A 
transaction is serializable and free of read/write conflicts if it's logically 
equivalent to one in which the two transactions ran one after the other, 
with no interleaving. 

The program figures out whether a transaction is serializable by modeling
it with a simple two-node graph structure and then searching for cycles in the 
graph. This is the standard algorithm described by Elmasri and Navathe in 
"Fundamentals of Database Systems." If it finds no cycles, the transaction 
is serializable. 

"""

import re # for regex matching
from sys import version_info # for checking user's version of Python
import sys 

# Set up global variables and check Python version
read_str = "read_item"
write_str = "write_item"

# Checks python version and redirects users on Python 2
if version_info[0] < 2:
    print("Please type 'scl enable rh-python36 bash' to activate Python 3.")
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
    
    # Break lists into first element and all the rest 
    x, *l1_tail = l1
    y, *l2_tail = l2
    
    # Recurse to generate all ordered combinations
    return [ [x] + l for l in combine_ordered(l1_tail, l2) ] + \
           [ [y] + l for l in combine_ordered(l2_tail, l1) ]


def start_program():
    """
    This function provides the user with the option to select default 
    transactions or supply their own. 
    """
    # Default schedules
    tr1 = "read_item(X); X:= X-N; write_item(X); read_item(Y); Y:= Y+N;write_item(Y)" 
    tr2 = "read_item(X); X:= X + M; write_item(X);"
    
    while True:
        user_input = input("Would you like to use the default transactions or "
                           "suppy your own? (1 for defaults, 2 for custom)\n") \
                           .lower()
        
        try:
            user_input = int(user_input)
        except:
            continue
        
        if user_input == 1:
            T_1 = list(filter(None, tr1.split(';'))) # split up default at semicolons
            T_2 = list(filter(None, tr2.split(';'))) 
            output_all_schedules(T_1, T_2)
            return
        elif user_input == 2:
            T_1 = get_transaction("1") # get two user-supplied transaction texts
            T_2 = get_transaction("2")
            output_all_schedules(T_1, T_2)
            return
        elif user_input not in (1, 2):
            continue
        
            
def get_transaction(ord):
    """
    Prompts the reader for transactions one and two.
    """
    while True:
        input_string = input("Please enter transaction {ord} as a single string "
                             "with semicolons between commands. Your transaction " 
                             "should contain the text 'read_item'.\n" \
                             .format(ord=ord)).lower()

        if "read_item" in input_string:
            T_1 = list(input_string.split(';')) # split at semicolon
            return T_1
        else:
            continue
        

def sch_to_dict(schedule, idx):
    """
    This function takes a schedule as text and returns a dictionary with all 
    of its relevant information.
    """
    sch = []
    s = re.compile("(?<=\()(.*?)(?=\))") # extract a string from between parentheses
    for idx, item in enumerate(schedule):
        
        if read_str in item or write_str in item: # spot transactions
            obj = s.search(item).group()
            t = {
                    'tr': item[:2],
                    'command': item[3:],
                    'order': idx + 1,
                    'obj': obj
                    }
            sch.append(t)
    sch = sorted(sch, key=lambda k: k['order'])
    return(sch)
    

def create_digraph(schedule):
    """
    This function takes a dictionary and returns a simple directed graph 
    structure with two nodes: T_1 and T_2. 
    
    Each node can contain an edge leading to the opposite node, or not. 
    
    The nested for loop here allows the function to look at the whole schedule
    from the point of view of transaction one and then transaction two. 
    """
    graph = {"T1": [], # initialize graph with two nodes
             "T2": []}
             
    for t in graph: # loop twice, once for each transaction
        write_token = [] # initialize token for writes
        read_token = [] # initialize token for reads
        
        if t == "T1": 
            t_not = "T2"
        else: 
            t_not = "T1"
            
        for tr in schedule: # Loop through the schedule to examine logic
            
            if tr['tr'] == t: 
                # If T_I has written, create write token
                if write_str in tr['command']:
                    write_token.append(tr['obj']) # Stores object of write as token
                # If T_I has read, create read token
                if read_str in tr['command']:
                    read_token.append(tr['obj']) # Stores object of read as token
            
            if tr['tr'] != t: # Check for conditions that affect serializability
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


def check_serial(schedules):
    """
    This function accepts a list of schedules and returns a list of dicts with
    information about their serializability. 
    
    Determines which directed graphs are serializable by checking them
    for cycles. 
    """
    lib = [] # stores one dict for each possible schedule of transactions
    
    for idx, schedule in enumerate(schedules):
        
        sch = sch_to_dict(schedule, idx) # returns a dict
        graph = create_digraph(sch) # returns a graph with nodes and edges
        
        if graph['T1'] == 'T2' and graph['T2'] == 'T1':
            serializable = "No"
        else:
            serializable = "Yes"
            
        lookup = {"idx": idx, 
                  "serializable": serializable}
        lib.append(lookup)
        
    return(lib)
    
    
def output_all_schedules(T_1, T_2):
    """
    Accepts two transaction schedules and combines them.
    
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
    
    # create a dictionary of serializability statuses for all schedules
    lib = check_serial(schedules)
    
    # For each possible schedule
    for idx, schedule in enumerate(schedules):
        T1_list = [] # list to store T1 transactions
        T2_list = [] # list to store T2 transactions
                  
        # for each transaction, separate T1s and T2s
        for item in schedule:
            if "T1" in item:
                T1_list.append(item)
                T2_list.append('')
            if "T2" in item:
                T2_list.append(item)
                T1_list.append('')
        
        # Look up current schedule's status
        for entry in lib:
            if entry['idx'] == idx:
                ans = entry['serializable']  
                
        # Print header
        print('\n%s\nSchedule: %s' % (h_line, idx))
        print('%-20s%-20s' % ("Transaction 1", "Transaction 2"))
        print(h_line)
         
        # Print all transactions in order 
        for i in range(0, len(schedule)):
            print('%-20s%-20s' % (T1_list[i][3:], T2_list[i][3:]))
            
        # Print serializability
        print(h_line)
        print("Serializable: " + ans)
        
        print("\n")
    return

start_program()
