#CN ASSIGNMENT 1
#FILE: server.py
#NAME: Zainab Mobin  CLASS: BESE 15-B  CMS: 514265

from socket import *
import threading #for thread locking

lock = threading.Lock() #
port = 12000
serverName = '192.168.1.6'
totalThreadCount = 0
runningThreadCount = 0
name_to_socket = dict() #maps connectionSocket against the username as the index


#USERNAME SETUP--------------------------------------------------------------------------------------------
#ensures username is unique and valid, returns accepted name
def setUniqueName(connectionSocket):
    while True:
        username = connectionSocket.recv(2048).decode() 
        
        # Invalid if the username has whitespace or '@' symbol
        if ' ' in username or '@' in username: 
            connectionSocket.send(str.encode('3'))
        
        #unique username or empty dictionary
        elif not name_to_socket or username not in name_to_socket: 
            connectionSocket.send(str.encode('2'))
            print(f"User {username} added to the chat")
            return username
        
        #duplicate username
        else: 
            connectionSocket.send(str.encode('3'))


#ONBOARDING MESSAGE--------------------------------------------------------------------------------------------
#explains the ways to communicate, shows users currently online and gives rules of naming
def sendInitialMessage(connectionSocket):
    message = (
    '\n                          Greetings! Welcome to the TCP chat.\n'
    '--------------------------------------------------------------------------------------------\n'
    '                                   ~ USER MANUAL ~\n'
    ' GROUP BROADCAST: send message normally to all active users in the group chat\n'
    ' DIRECT MESSAGE: Tag a user with the @ symbol to message \n QUIT: Type "/quit" to leave the chat\n'
    '--------------------------------------------------------------------------------------------\n'
    '                                   ~ USERS ONLINE ~')
    message += getOnlineUsers() #display online/active users
    message += ('\n--------------------------------------------------------------------------------------------\n'
    '                                   ~ NAMING RULES ~\n'
    ' Type a unique username so others communicate with you on the network.\n'
    ' It can have symbols and alphanumeric characters but not spaces or the symbol @\n'
    '>> Your Name: ')
    connectionSocket.send(message.encode())
    
    
#Gets list of online users
def getOnlineUsers():
    list = ''
    if not name_to_socket:
        list = '\n   [No users online at the moment :( ]'
    else:
        for username in name_to_socket:
            list += '\n ' + username 
    return list


#checks if user is registered
def isRegistered(username):
    if username in name_to_socket:
        return True
    return False


#OVERLOADED FUNCTION FOR MULTICASTING
# if a username is included, message is not sent to that user
# else, multicasts message to all
def multicastMessage(message, username=None):
    with lock: #lock added to limit simultaneous access by multiple threads
        for name in name_to_socket:
            if username and name == username: #Dont broadcast message back to sender (reduces redundancy)
                continue
            name_to_socket[name].send(message.encode()) #send message to all users


#CREATE SERVER PORT AND GET IT RUNNING--------------------------------------------------------------------------------------------
try:
    serverSocket = socket(AF_INET, SOCK_STREAM)
    print("Server Socket created successfully")
except socket.error as e:
    print("Encountered error while creating server socket: ", e)

try:
    serverSocket.bind((serverName, port))
    print("Server Socket binded to port successfully")
except socket.error as e:
    print("Failed to bind socket to port: ", e)

serverSocket.listen(2) #listen to upto 10 connections
print("Waiting for connections")


#CLIENT CONNECTION THREAD---------------------------------------------------------------------------------------------------------------
def createClientThread(connectionSocket, connectionAddress):
    global totalThreadCount, runningThreadCount,  name_to_socket #declared to be global variables for recognition inside the funtion

    connectionSocket.send(str.encode('1')) #initial handsake between client and server
    ack = connectionSocket.recv(2048).decode() 
    if ack == "1RDY": #recieves ack from client 
        sendInitialMessage(connectionSocket) #sends onboarding message to client
    username = setUniqueName(connectionSocket) #get client's username
    name_to_socket[username] = connectionSocket #insert connectionSocket against username
    multicast_message = '--------------------------------@' + username + ' has entered the chat--------------------------------'
    multicastMessage(multicast_message) #multicast joining notification to all

    # start while loop, set unique username (check uniqueness with name_to_socket), then send initial message
    while True:
       
        message = connectionSocket.recv(2048).decode()

        #user wants to quit
        if message  == '/quit':
            runningThreadCount -= 1 #decrease current threads by one
            print(f"Disconnecting with client @{username} at IP {connectionAddress[0]} at port {connectionAddress[1]}")
            multicast_message = '--------------------------------@' + username + ' has left the chat--------------------------------'
            multicastMessage(multicast_message) #multicasts leaving notification @this_guy left
            
            with lock: #put lock so client is deleted first and no random message is sent during this process   
                del name_to_socket[username] #delete username/connectionSocket entry from the dict()
            connectionSocket.send(str.encode('0')) #code for /quit sent to client
            connectionSocket.close()
            break

        #check for @ unicast
        elif message[0] == '@':
            parts = message.split(' ')
            recipient = parts[0][1:] #takes first part from the message, '@Bravo', removes @ to get reciever name
            if not isRegistered(recipient): #checks if recipient is registered
                connectionSocket.send(str.encode('4'))
            else:
                recipient_len = len(recipient)+1 # length(recipient name) + length('@') 
                recipient_msg =(
                ' <<< PRIVATE MESSAGE >>>\n'
                ' \t@'+username+' -> @'+recipient+': '+ message[recipient_len:]) # removes the first n characters from a string
                #remove the recipient name from the message to get the actual text
                name_to_socket[recipient].send(recipient_msg.encode())
        
        #message assumed to be multicast
        else:
            #if len(name_to_socket) > 1: #people other that the sender
            message = ' @'+username+" : "+message; # ' @Zainab : How's everyone?'
            multicastMessage(message, username)


#MAIN SERVER LOOP-------------------------------------------------------------------------------------------------------------
while True: #establish connections with other clients 
    connectionSocket, connectionAddress = serverSocket.accept()
    print(f"Established connection with IP {connectionAddress[0]} at port {connectionAddress[1]}")
    thread = threading.Thread(target=createClientThread,args=(connectionSocket,connectionAddress,)) 
    #target function is passed as an instance instead of a function, parameters passed as values in a tuple
    thread.start()
    totalThreadCount += 1
    runningThreadCount += 1
    print("Total Created Threads: ", totalThreadCount)
    print("Running Threads: ", runningThreadCount)


#RETURN CODE REFERENCE--------------------------------------------------------------------------------------------------------
# 0: client '/quit' -> server terminates client connection
# 1: server -> client ready for onboarding
# 1RDY: client acknowledgment -> server
# 2: valid username
# 3: invalid/duplicate username
# 4: unregistered recipient