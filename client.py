import socket, sys

BUFFER_SIZE = 1024

byteFiles = (".ico", ".jpg") # which file extensions are returned as bytes and not text

def createFile(userRequest, data):
    if userRequest == "/":
        userRequest = "index.html"
    elif userRequest == "/redirect":
        userRequest = "result.html"
    else:
        userRequest = userRequest[userRequest.rfind('/')+1:]
        
    if userRequest.endswith(byteFiles):
        with open(userRequest, "wb") as file:
            file.write(data)
    else:    
        with open(userRequest, "w") as file:
            file.write(data.decode())
            
def getFromServer(serverSocket, userRequest):
    getMessage = "GET " + userRequest + " HTTP/1.1\n"
    getMessage+= "Connection: close\r\n\r\n"
    serverSocket.send(getMessage.encode())
    
    startOfFirstLine = serverSocket.recv(12).decode() # should only contain HTTP/1.1 (code)
    code = startOfFirstLine[9:] # should only contain the code number
    
    if code == "404":
        restOfFirstLine = serverSocket.recv(11).decode()
        print(startOfFirstLine + restOfFirstLine, end='')
        return # we don't create a file in this case...
    elif code == "301":
        restOfFirstLine = serverSocket.recv(19).decode()
        serverSocket.recv(18) # also receive the connection line
        
        location = '' # get the location
        while True:
            data = serverSocket.recv(BUFFER_SIZE).decode()
            location+= data
            if data.endswith("\n\n"):
                break
        
        location = location[10:].strip()
        print(startOfFirstLine + restOfFirstLine, end='')
        
        redirectSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        redirectSocket.connect(serverSocket.getpeername())
        getFromServer(redirectSocket, location) # dont do it statically... get the name of the file from the location line
        
        return
    
    restOfFirstLine = serverSocket.recv(4).decode() # OK\n
    print(startOfFirstLine + restOfFirstLine, end='')
    
    line = serverSocket.recv(13).decode() # Connection: (c or k)
    if line[12] == 'c': 
        serverSocket.recv(5) # lose\n
    else:
        serverSocket.recv(10) # eep-alive\n
        
    serverSocket.recv(16) # Content-Length: 
    
    data = b''
    while True:
        chunk = serverSocket.recv(BUFFER_SIZE)
        if not chunk:
            break

        if b"\n" in chunk:
            before_newline, after_newline = chunk.split(b"\n", 1)
            data += after_newline[1:]
            break  # Stop processing contentLength

    # Continue reading the rest of the data if needed
    while True:
        chunk = serverSocket.recv(BUFFER_SIZE)
        if not chunk:
            break
        data += chunk
        
    createFile(userRequest, data) # skip the first \n

def main():
    ip = sys.argv[1]
    port = int(sys.argv[2])
    
    while True:
        userRequest = input()
        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, port))
        getFromServer(s, userRequest)
        s.close()
        
    
if __name__ == "__main__":
    main()