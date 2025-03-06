# Custom HTTP Client and Server In Python
In my Computer Networks course I had to write a basic HTTP/1.1 server + client in python.
# Features
Supports sending textual files and image files from the server to a client in HTTP format, meaning it can send images or html pages to be shown in browsers.
# Server
To setup the server just run the server script using: `python3 server.py PORT`.
It will then create the server at that port, which will wait for HTTP requests.
If an HTTP request is processed, it expects the desired resource to be inside the files folder.
Example: if a request to `/a/b.html` is received, the server tries to find `files/a/b.html`.
# Client
You can of course connect to the Server using a browser, but you can also use the provided client program.
In order to run it use: `python3 client.py SERVER_IP SERVER_PORT`.
Then, you can enter to the terminal a desired file path. Successful files that were downloaded from the server will be saved locally in the same folder as the client script.
# Notes
This is just a simple homework part from my course which focuses on computer networks, so the server is currently single threaded (but limits each connection to 1 second). 
Also, there is no way to upload a file to the server remotely from a client.
Lastly, the server only supports sending JPEG (.jpg) and Icons (.ico) images. The other format are considered texts instead.
