#Lindon Jonathan Sanley dos Santos Pereira Monroe
#Simulated Call Center Application
#Call center queue manager who receives commands - Server

from email import message
from twisted.internet import reactor, protocol
import time
from cmd import Cmd
from collections import deque


class callCenter(Cmd):
    def __init__(self, operator_array, protocol):

        self.protocol=protocol
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
            returned_str= 'Call '+ call_id+' received' 
            returned_str2=redirect_call(self, call_id)
            if (returned_str2):
                return returned_str+'\n'+returned_str2
            else:     
                return returned_str+'\n'+'Call '+ call_id+' waiting in queue'

        else:
            return("Call id already in use.")
    
    #answers the call for the corresponding operator
    def do_answer(self, op): #op is the operator
        if (op in self.operator_array):
            if (self.op_state_and_call[op][0]=='ringing'):  #if there's a call ringing for the operator
                associate_operators_states_calls(self, op, 'busy', self.op_state_and_call[op][1])
                return ('Call '+self.op_state_and_call[op][1]+ ' answered by operator '+op)
            else:
                return ("No call ringing for this operator.")
        else:
            return ("No corresponding operator id.")

    #this functions rejects a ringing call
    #maybe there's an error in the item 13 of the "tests" section
    #it says call 5 rejected by operator A , call 5 ringing for operator A
    #it should be ringing for operator B
    def do_reject(self, op): #op is the operator
        if (op in self.operator_array):
            if (self.op_state_and_call[op][0]=='ringing'):  #if there's a call ringing for the operator
                returned_str= 'Call '+ self.op_state_and_call[op][1]+ ' rejected by operator '+ op
                returned_str2=reject_call(self, op, self.op_state_and_call[op][1]) 
                returned_str3=check_rejected_queue(self)   #checks if there's some rejected_call to ring
                returned_str4=check_waiting_queue(self)   #checks if there's some waiting_call to ring
                if (returned_str2):
                    returned_str+='\n'+returned_str2
                if (returned_str3):
                    returned_str+='\n'+returned_str3
                if (returned_str4):
                    returned_str+='\n'+returned_str4
                return returned_str
            else:
                return ("No call ringing for this operator.")
        else:
            return ("No corresponding operator id.")

    #hangs up the call, taking in consideration if it's in the rejected queue, the waiting queue, ringing or answered 
    def do_hangup(self, call_id): 
        try:
            if (self.call_and_op[call_id]=='queue'):
                del self.waiting_queue[self.waiting_queue.index(call_id)]
                return ('Call '+ call_id +' missed')
            elif (self.call_and_op[call_id]=='rejected'):
                del self.rejected_queue[self.rejected_queue.index(call_id)]
                return ('Call '+call_id+' missed')
            elif (self.op_state_and_call[self.call_and_op[call_id]][0]=='ringing'):
                hangup_call(self, self.call_and_op[call_id], call_id)
                returned_str= 'Call '+ call_id+ ' missed'
                returned_str2=check_rejected_queue(self)
                returned_str3=check_waiting_queue(self)
                if (returned_str2):
                    returned_str+='\n'+returned_str2
                if (returned_str3):
                    returned_str+='\n'+returned_str3
            else: 
                returned_str='Call '+ call_id+ ' finished and operator '+ self.call_and_op[call_id]+' available'
                hangup_call(self, self.call_and_op[call_id], call_id)
                returned_str2=check_rejected_queue(self)
                returned_str3=check_waiting_queue(self)
                if (returned_str2):
                    returned_str+='\n'+returned_str2
                if (returned_str3):
                    returned_str+='\n'+returned_str3
            return returned_str
        except KeyError:
            return ("No corresponding call id.")


#checks if there's some rejected call to ring, and then redirects it to see if there's an operator available. 
#if there's an operator available, the rejected call is removed from the deque
def check_rejected_queue(callCenter_obj): 
    if (len(callCenter_obj.rejected_queue)):
        returned_str=redirect_rejected_or_waiting_call(callCenter_obj, callCenter_obj.rejected_queue[0])
        if (returned_str):
            callCenter_obj.rejected_queue.popleft()
            return returned_str
    return 0

#checks if there's some waiting call to ring, and then redirects it to see if there's an operator available. 
#if there's an operator available, the waiting call is removed from the deque
def check_waiting_queue(callCenter_obj): 
    if (len(callCenter_obj.waiting_queue)):
        returned_str=redirect_rejected_or_waiting_call(callCenter_obj, callCenter_obj.waiting_queue[0])
        if (returned_str):
            callCenter_obj.waiting_queue.popleft()
            return returned_str
    return 0

#if there's an operator available, the call rings for him if not, the call goes to the queue
def redirect_call(callCenter_obj, call_id):
    for i in callCenter_obj.operator_array:
        if callCenter_obj.op_state_and_call[i][0]=='available':
            associate_operators_states_calls(callCenter_obj, i, 'ringing', call_id)
            reactor.callInThread(callCenter_obj.protocol.ignore, i, call_id)
            return 'Call '+ call_id +' ringing for operator '+ i
        
    associate_operators_states_calls(callCenter_obj, 'queue', 'no state', call_id)
    callCenter_obj.waiting_queue.append(call_id)
    #print('\nCall', call_id, 'waiting in queue')
    return 0

#if there's an operator available, the rejected call rings for him
def redirect_rejected_or_waiting_call(callCenter_obj, call_id):
    for i in callCenter_obj.operator_array:
        if callCenter_obj.op_state_and_call[i][0]=='available':
            associate_operators_states_calls(callCenter_obj, i, 'ringing', call_id)
            reactor.callInThread(callCenter_obj.protocol.ignore, i, call_id)
            return 'Call '+ call_id+ ' ringing for operator '+ i
    return 0

#updates dicts if the call is redirected to an operator or the waiting queue
def associate_operators_states_calls(callCenter_obj, op, status, call_id):
    callCenter_obj.op_state_and_call[op]=[status, call_id]
    callCenter_obj.call_and_op[call_id]=op
    return

#puts the call in the refected deque and updates dicts if the call is rejected 
def reject_call(callCenter_obj, op, call_id):
    callCenter_obj.rejected_queue.append(callCenter_obj.op_state_and_call[op][1])  #puts rejected call in the rejected calls deque
    returned_str=check_rejected_queue(callCenter_obj)  #checks if theres some rejected_call to ring
    callCenter_obj.op_state_and_call[op]=['available', 'no call'] #only after redirecting the rejected call the operator appears as available
    callCenter_obj.call_and_op[call_id]='rejected'
    return returned_str

#updates dicts if the call is hangup
def hangup_call(callCenter_obj, op, call_id):
    callCenter_obj.op_state_and_call[op]=['available', 'no call']
    del callCenter_obj.call_and_op[call_id]
    return


#### The specific server part starts here

class EchoServer(protocol.Protocol):
    def __init__(self, factory):
        self.sCC=callCenter(['A', 'B'], self) #instantiating our simulated call center and passing operator array
        self.factory=factory

    def dataReceived(self, data):
        data=data.decode()
        aux1=data.split()[1].replace('"','')
        aux1=aux1.replace(',','')
        aux2=data.split()[3].replace('"','')
        aux2=aux2.replace('}','')
        aux1=aux1+' '+aux2
        self.sendMessage(self.sCC.onecmd(aux1))

    def sendMessage(self,data):
        message='{"response": "'+data+'"}'
        message=message.encode()
        self.transport.write(message)

    #this function is activated when a call starts ringing
    def ignore(self, i, call):
        time.sleep(10)  #waits 10 seconds after starts ringing to verify if it's still ringing
        if (call in self.sCC.call_and_op and self.sCC.op_state_and_call[i][0]=='ringing'):  #if there's a call ringing for the operator
            aux1='Call '+ call+ ' ignored by operator '+ i
            hangup_call(self.sCC, self.sCC.call_and_op[call], call)
            returned_str2=check_rejected_queue(self.sCC)
            returned_str3=check_waiting_queue(self.sCC)
            if (returned_str2):
                aux1+='\n'+returned_str2
            if (returned_str3):
                aux1+='\n'+returned_str3
            self.sendMessage(aux1)

class ServerFactory(protocol.Factory):

    def buildProtocol(self, addr):
        return EchoServer(self)

def main():
    reactor.listenTCP(5678, ServerFactory())    #This runs the protocol on port 5678
    reactor.run() 

# this only runs if the module was *not* imported
if __name__ == "__main__":
    main()
