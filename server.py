import socket, sys, os

BUFFER_SIZE = 1024

byteFiles = (".ico", ".jpg") # which file extensions are returned as bytes and not text

def formatSendMessage(code, connection, data, isBinary):
    sendData = "HTTP/1.1 " + code + "\n"
    
    if code == "404 Not Found":
        sendData+= "Connection: close\n\n"
        return sendData.encode()
    elif code == "301 Moved Permanently":
        sendData+= "Connection: close\n"
        sendData+= "Location: /result.html\n\n"
        return sendData.encode()
            
    sendData+= "Connection: " + connection + "\n"
    sendData+= "Content-Length: " + str(len(data)) + "\n"
    sendData+= "\n" # the end of the header
    
    if isBinary:
        return sendData.encode() + data # the data is already in bytes, we just need to ncode the header.
    else:
        return (sendData + data).encode() # both the data and the header are strings that need to be encoded.
    

def loadBytesFile(filePath):
    with open(filePath, 'rb') as file:
        return file.read()
    

def loadTextFile(filePath):
    with open(filePath, 'r', encoding='utf-8') as file:
        return file.read()
        
def loadFile(filePath):
    if len(filePath) > 0 and filePath[0] != '/':
        filePath = "/" + filePath
    code = "200 OK"
    if filePath == '/':
        filePath = "./files/index.html"
    elif filePath == '/redirect':
        return ("301 Moved Permanently", "/result.html", False)
    else:
        filePath = "./files" + filePath
        if not os.path.exists(filePath) or not os.path.isfile(filePath):
            return ("404 Not Found", None, False)
            
    # Handle byteFiles (images and such) and text files differently:
    if filePath.endswith(byteFiles):
        return (code, loadBytesFile(filePath), True)
    
    return (code, loadTextFile(filePath), False)

def handleClient(clientSocket, clientAddress):
    clientSocket.settimeout(1) # each socket opperation is limited to 1 second.
    
    while True: #each iteration here is a full interaction between the server and the client:
        data = b''
        while True: # Get the complete data from multiple chunks (the message can be received in parts):
            try:
                chunk = clientSocket.recv(BUFFER_SIZE)
                if not chunk: # if we received no data, we finished reading the request
                    break
                
                data+= chunk # we have data to add, then add it

                if chunk.endswith(b"\r\n\r\n"): # if this is the end of the transmission
                    break
            except socket.timeout: # if we had a timeout then we should go to the next client...
                return
            
        if len(data) == 0:
            return # this means this entire request was empty...

        # Extract the file we need to load and the connection type from the message:
        data = data.decode()
        print(data, end='')
        data = data.split("\n")
        importantLines = [line for line in data if line.startswith(("GET", "Connection:"))]
        fileToLoad = importantLines[0].split()[1]
        connectionType = importantLines[1].split()[1]

        # Load the file itself (and find the return code):
        code, fileData, isBinary = loadFile(fileToLoad)

        # Format this information as needed and send it:
        sendData = formatSendMessage(code, connectionType, fileData, isBinary)
        clientSocket.send(sendData)
        
        # We close the connection when specified to:
        if connectionType == "close":
            return

def main():
    # Setup:
    port = int(sys.argv[1])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(100)
    
    # Program loop:
    while True:
        clientSocket, clientAddress = s.accept()
        handleClient(clientSocket, clientAddress)
        clientSocket.close()
        

if __name__ == "__main__":
    main()