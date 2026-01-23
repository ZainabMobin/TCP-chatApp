# CN ASSIGNMENT 1
# FILE: client.py
# NAME: Zainab Mobin  CLASS: BESE 15-B  CMS: 514265

from socket import * #for socket programming
import threading #for multithreading
import time #for delayed re-connection request sent to the server 
import  sys # for sys.stdout functions to manually write to the terminal
import msvcrt #microsoft visual C runtime library, for the use of kbhit() for live input logging
 

serverName = '192.168.1.6'
serverPort = 12000
resend_time = 5 #delay after which server is requested again
username = ''
terminateProgram = False #external bool that controls the main loop
input_buffer = "" #string for manual keystroke logging 
lock = threading.Lock() #enables only one socket to access a resource at a time 


#PRINTS INCOMING MESSAGES AND INPUT BUFFER
def safe_print(message):
    global input_buffer
    with lock: #limits one thread to utilize this at a single time, preventing race condition
        sys.stdout.write('\r' + ' ' *(len(input_buffer)+1) + '\r') #overwrite the terminal with empty spaces (number of whitespaces equal to the length of already typed message + 1 char for the initial '-')
        sys.stdout.write(message + '\n-'+input_buffer) #on the overwritten line, display the message, go to next line and display the typed message from the input_buffer
        sys.stdout.flush()


#SEND REQUEST TO THE SERVER-----------------------------------------------------------
def sendRequestThread(clientSocket): 
    global input_buffer
    while True: 
        if msvcrt.kbhit(): #checks if keyboard has been hit
            key = msvcrt.getwch() #gets the key that has been pressed
            # enter is key pressed,
            if key == '\r': #send the message to the server
                if (len(input_buffer) > 0): #prevents sending of empty messages
                    clientSocket.send(input_buffer.encode())
                    input_buffer = "" #reset input buffer
                    safe_print("")
            # backspace pressed
            elif key == '\x08':
                if len(input_buffer)>0: #only delete the characters from the input buffer, prevents overwriting of already present terminal text
                    input_buffer = input_buffer[:-1] #delete last character from the input_buffer string
                    sys.stdout.write('\b \b') #visually replace that character with an empty space on the terminal to simulate the backspace effect on a typed string
                    sys.stdout.flush()
            # normal key pressed
            else:
                input_buffer = input_buffer + key #concatenates character on the string
                sys.stdout.write(key) #display key to simulate real time typing
                sys.stdout.flush()


#GET RESPONSE FROM THE SERVER-----------------------------------------------------------
def getResponseThread(clientSocket):
    global terminateProgram
    while True:
        try:
            response = clientSocket.recv(2048).decode()
            # 0 - Client requests termination
            if response == '0': #error code sent to terminate connection
                safe_print("Terminating Connection...")
                clientSocket.close()
                terminateProgram = True
                break
            # 1 - Server ready to send initial onboarding message
            elif response == '1': # get initial/onboarding messages and initialize username
                clientSocket.send('1RDY'.encode()) #acknowledgement readiness (client is ready to recieve initial message)
                safe_print(clientSocket.recv(2048).decode()) #recieve and print initial message from server.
            # 2 - Client Username accepted
            elif response == '2':
                safe_print("Username Accepted!")
            # 3 - Invalid Username
            elif response == '3':
                safe_print("Error, Please select a username that follows the naming rules!\nEnter a unique username:")
            # 4 - recipient not found
            elif response == '4':
                safe_print("Error, Recipient either left the chat or is not registered.")
            # Actual message sent by the server (unicast or multicast)
            else:
                safe_print(response)
        except OSError as e:
            safe_print("Error getting response for server: ", e)
            time.sleep(resend_time)
            break #break out of loop if error triggered


#MAIN CONTROL LOOP-----------------------------------------------------------------------
while True:
    if terminateProgram: 
        break
    
    #Permission to connect to chat 
    user_input = input("Connect to a TCP group chat? (y/n): ")
    if user_input.lower() == 'y':
        try:
            clientSocket = socket(AF_INET, SOCK_STREAM) #create new socket for every connection
            clientSocket.connect((serverName, serverPort)) #connect to server
            safe_print("Client Socket successfully created and connected to server!")
        except OSError as e:
            safe_print("Error creating client socket: ", e)
            time.sleep(resend_time)
            continue #attempt to create client socket again after a timeout to not overwhelm the server with connection requests
        
        response = threading.Thread(target=getResponseThread, args=(clientSocket,)) #gets response from server
        request = threading.Thread(target=sendRequestThread,daemon=True, args=(clientSocket,)) #sends messages to server, set to daemon thread i.e. when all other threads end(getResponseThread in this case), this thread is automatically stopped by the program
        
        #start both threads
        response.start()
        request.start()
        #join both threads for clean disconnection of socket when threads stop
        response.join()
        safe_print('Successfully Disconnected') #printed when all threads stop running i.e. user exits chat
    
    # pressed 'n'
    elif user_input.lower() == 'n':
        safe_print("Exiting program...")
        break
    
    # random input prompts reconnection menu to come up after a time delay
    else:
        safe_print("Please enter a valid letter")
        time.sleep(resend_time) #present choice after resend_time seconds