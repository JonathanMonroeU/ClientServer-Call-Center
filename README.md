# Simulated Call Center using a TCP Client and a TCP Server 

#### There are 2 versions of this simulation. 
- Basic: Uses the cmdloop method from Cmd to receive instructions and then print the consequences of that instruction on the Call Center. 
- Advanced: Has the same logic from the basic implementation, but uses a TCP Client to receive commands directly from stdin, turn them into JSON, and send them to a TCP Server. This server calls Cmd.onecmd (Bonus Task 2) and manages the Call Center accordingly, sending the feedback to the client. Also, when a call keeps ringing for 10 seconds without being answered, it's ignored using the reactor.callInThread method (Bonus Task 1).
    - The Docker Hub repository of the advanced version (Bonus Task 3) can be found here: [Docker Hub Repository](https://hub.docker.com/repository/docker/jonathanspmonroe/call-center-client-server/) 
#### There are 5 instructions, in total:
- call [call id]: makes application receive a call whose id is <id>
- answer [operator id]: makes operator <id> answer a call being delivered to it
- reject [operator id]: makes operator <id> reject a call being delivered to it
- hangup [call id]: makes call whose id is <id> be finished
- quit (exclusively on the basic version)


