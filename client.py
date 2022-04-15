#Lindon Jonathan Sanley dos Santos Pereira Monroe
#Simulated Call Center Application
#Command Interpreter - Client

from twisted.internet import reactor, protocol, stdio
from twisted.protocols.basic import LineReceiver

### a client protocol
class LnRcv(LineReceiver):
    #from os import linesep as delimiter   
    def __init__(self, protocol):
        self.protocol = protocol
    delimiter='\n' 

    def dataReceived(self, data):
        if data.split()[0].decode() != '{"response":':  #it's meant to enter here, it's the data coming from stdin
            data=data.decode()
            try:
                a=data.split()[0]
                b=data.split()[1]
                c='{"command": "'+a+'", "id": "'+b+'"}'
                c=c.encode()
                self.protocol.sendData(c) 
            except:
                print("Not a valid instruction format.")

        else:
            data=data.decode()
            a=data.replace('{"response": "','')
            a=a.replace('"}','')
            print(a)

    def connectionLost(self, reason):
        print("connection lost") #7

class EchoProtocol(protocol.Protocol):
    def __init__(self, factory):
        self.factory = factory
        stdio.StandardIO(LnRcv(self))
    def sendData(self, data):
        self.transport.write(data)
    def dataReceived(self, data):
        if data.split()[0].decode() != '{"response":':
            data=data.decode()
            a=data.split()[0]
            b=data.split()[1]
            c='{"command": "'+a+'", "id": "'+b+'"}'
            c=c.encode()
            self.protocol.sendData(c) 
        else:       #it's meant to enter here, it's the data coming from the server
            data=data.decode()
            a=data.replace('{"response": "','')
            a=a.replace('"}','')
            print(a)
        #self.transport.loseConnection()

class EchoFac(protocol.ClientFactory):    
    def buildProtocol(self, addr):
        return EchoProtocol(self)
        
    def clientConnectionFailed(self, connector, reason):
        print("Connection failed - goodbye!")
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        print("Connection lost - goodbye!") #8
        reactor.stop()


# this connects the protocol to a server running on port 5678
def main():
    reactor.connectTCP("localhost", 5678, EchoFac()) #1
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == "__main__":
    main()
