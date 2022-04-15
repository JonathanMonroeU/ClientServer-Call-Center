#Lindon Jonathan Sanley dos Santos Pereira Monroe
#Simulated Call Center Application

from cmd import Cmd
from collections import deque


class callCenter(Cmd):
    def __init__(self, operator_array):
        super(callCenter, self).__init__()
        self.operator_array = operator_array #chosen list of operators
        self.op_state_and_call  = dict () #op_state_and_call={'op':['state', 'call']}
        self.call_and_op  = dict () #call_and_op={'call':'op'}

        for i in self.operator_array:
            self.op_state_and_call[i]=['available', 'no call']  #start operators as available
        #the trigger for cheching if theres someone available to take the waiting and rejected calls is when any operator gets available
        self.waiting_queue = deque ([])  #deque for waiting calls
        self.rejected_queue = deque([])  #deque for rejected calls

    #sends the call to being redirected
    def do_call(self, call_id): 
        if (call_id not in self.call_and_op):
            print('Call', call_id,'received')  
            redirect_call(self, call_id)
        else:
            print("Call id already in use.")
    
    #answers the call for the corresponding operator
    def do_answer(self, op): #op is the operator
        if (op in self.operator_array):
            if (self.op_state_and_call[op][0]=='ringing'):  #if there's a call ringing for the operator
                print ('Call', self.op_state_and_call[op][1], 'answered by operator', op)
                associate_operators_states_calls(self, op, 'busy', self.op_state_and_call[op][1])
            else:
                print("No call ringing for this operator.")
        else:
            print("No corresponding operator id.")

    #this functions rejects a ringing call
    #maybe there's an error in the item 13 of the "tests" section
    #it says call 5 rejected by operator A , call 5 ringing for operator A
    #it should be ringing for operator B if he was available
    def do_reject(self, op): #op is the operator
        if (op in self.operator_array):
            if (self.op_state_and_call[op][0]=='ringing'):  #if there's a call ringing for the operator
                print ('Call', self.op_state_and_call[op][1], 'rejected by operator', op)
                reject_call(self, op, self.op_state_and_call[op][1]) 
                check_rejected_queue(self)
                check_waiting_queue(self)   #checks if there's some waiting_call to ring

            else:
                print("No call ringing for this operator.")
        else:
            print("No corresponding operator id.")

    #hangs up the call, taking in consideration if it's in the rejected queue, the waiting queue, ringing or answered 
    def do_hangup(self, call_id): 
        try:
            if (self.call_and_op[call_id]=='queue'):
                del self.waiting_queue[self.waiting_queue.index(call_id)]
                print ('Call', call_id, 'missed')
            elif (self.call_and_op[call_id]=='rejected'):
                del self.rejected_queue[self.rejected_queue.index(call_id)]
                print ('Call', call_id, 'missed')
            elif (self.op_state_and_call[self.call_and_op[call_id]][0]=='ringing'):
                hangup_call(self, self.call_and_op[call_id], call_id)
                print ('Call', call_id, 'missed')
                check_rejected_queue(self)
                check_waiting_queue(self)
            else: 
                print ('Call', call_id, 'finished and operator', self.call_and_op[call_id], 'available')
                hangup_call(self, self.call_and_op[call_id], call_id)
                check_rejected_queue(self)
                check_waiting_queue(self)
        except KeyError:
            print("No corresponding call id.")

    def do_quit(self, args):
        """Quits the program."""
        print ("Quitting.")
        raise SystemExit

#checks if there's some rejected call to ring, and then redirects it to see if there's an operator available. 
#if there's an operator available, the rejected call is removed from the deque
def check_rejected_queue(callCenter_obj): 
    if (len(callCenter_obj.rejected_queue)):
        if redirect_rejected_or_waiting_call(callCenter_obj, callCenter_obj.rejected_queue[0]):
            callCenter_obj.rejected_queue.popleft()
    return

#checks if there's some waiting call to ring, and then redirects it to see if there's an operator available. 
#if there's an operator available, the waiting call is removed from the deque
def check_waiting_queue(callCenter_obj):
    if (len(callCenter_obj.waiting_queue)):
        if redirect_rejected_or_waiting_call(callCenter_obj, callCenter_obj.waiting_queue[0]):
            callCenter_obj.waiting_queue.popleft()
    return

#if there's an operator available, the call rings for him if not, the call goes to the queue
def redirect_call(callCenter_obj, call_id):
    for i in callCenter_obj.operator_array:
        if callCenter_obj.op_state_and_call[i][0]=='available':
            associate_operators_states_calls(callCenter_obj, i, 'ringing', call_id)
            print('Call', call_id, 'ringing for operator', i)
            return 1
        
    associate_operators_states_calls(callCenter_obj, 'queue', 'no state', call_id)
    callCenter_obj.waiting_queue.append(call_id)
    print('Call', call_id, 'waiting in queue')
    return 0

#if there's an operator available, the rejected call rings for him
def redirect_rejected_or_waiting_call(callCenter_obj, call_id):
    for i in callCenter_obj.operator_array:
        if callCenter_obj.op_state_and_call[i][0]=='available':
            associate_operators_states_calls(callCenter_obj, i, 'ringing', call_id)
            print('Call', call_id, 'ringing for operator', i)
            return 1
    return 0

#updates dicts if the call is redirected to an operator or the waiting queue
def associate_operators_states_calls(callCenter_obj, op, status, call_id):
    callCenter_obj.op_state_and_call[op]=[status, call_id]
    callCenter_obj.call_and_op[call_id]=op
    return

#puts the call in the refected deque and updates dicts if the call is rejected 
def reject_call(callCenter_obj, op, call_id):
    callCenter_obj.rejected_queue.append(callCenter_obj.op_state_and_call[op][1])  #puts rejected call in the rejected calls deque
    check_rejected_queue(callCenter_obj)  #checks if theres some rejected_call to ring
    callCenter_obj.op_state_and_call[op]=['available', 'no call'] #only after redirecting the rejected call the operator appears as available
    callCenter_obj.call_and_op[call_id]='rejected'
    return

#updates dicts if the call is hangup
def hangup_call(callCenter_obj, op, call_id):
    callCenter_obj.op_state_and_call[op]=['available', 'no call']
    del callCenter_obj.call_and_op[call_id]
    return

def main():
    simulatedCallCenter=callCenter(['A', 'B']) #instantiating our simulated call center and passing operator array
    simulatedCallCenter.cmdloop()
    return

if __name__ == '__main__': #starting main function if this is being use as the main .py
    main()