import socket
import ssl
import os
import sys
import warnings


def send_image_and_format(image_path, image_format, server_address, server_port,option,new_size = None):
    
    basename = os.path.basename(image_path)
    image_name = os.path.splitext(basename)[0]
    with open(image_path, 'rb') as f:
        image_data = f.read()
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS)  
    ssl_context.verify_mode = ssl.CERT_NONE  
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
      with ssl_context.wrap_socket(client_socket, server_hostname=server_address) as ssl_socket: 
       try: 
        ssl_socket.connect((server_address, server_port))
        ssl_socket.sendall(len(image_data).to_bytes(4, byteorder='big'))
        ssl_socket.sendall(image_data)
        ack = ssl_socket.recv(1024)
        if ack != b'ACK':
                print('Error: Server did not acknowledge receipt of image data')
                return
        
       except Exception as e:
            print(f"Error occurred: {e}")
       
       ssl_socket.sendall(option.encode())
       ack = ssl_socket.recv(1024)
       if ack != b'ACK':
                print('Error: Server did not acknowledge receipt of image data')
                return
       
       if option == "convert":
        ssl_socket.sendall(image_format.lower().encode())
       elif option == "compress":
           ssl_socket.sendall(image_format.lower().encode())
           ack = ssl_socket.recv(1024)
           if ack != b'ACK':
                print('Error: Server did not acknowledge receipt of image data')
                return
           
          
           ssl_socket.sendall(new_size.encode())
        
       converted_image_data = b''
       while True:
            chunk = ssl_socket.recv(4096)
            if not chunk:
                break
            converted_image_data += chunk

       if option == "convert":
        with open(f"NEW_{image_name}." + image_format.lower(), 'wb') as f:
            f.write(converted_image_data)
            print(f'\033[92mImage conversion completed successfully!\033[0m')
       elif option == "compress":
        with open(f"NEW_{image_name}." + image_format.lower(), 'wb') as f:
            f.write(converted_image_data)
            print(f'\033[92mImage compressed successfully!\033[0m')   
       elif option == "removebg":
           with open(f"NEW_{image_name}.png", 'wb') as f:
            f.write(converted_image_data)
            print(f'\033[92mBackground removed successfully!\033[0m')
           


server_address = 'localhost'
server_port = 8888


image_path = input("\033[96mEnter the path of the image file: \033[0m")
while(not os.path.isfile(image_path)):
    print("\033[91mFile does not exist.\033[91m")
    image_path = input("\033[96mEnter the path of the image file: \033[0m")
    
option = input("\033[96mEnter option (compress/convert/removebg) or exit: \033[0m").lower()
while(option not in ['compress','convert', 'removebg','exit']):
    print("\033[91mInvalid option.\033[91m")
    option = input("\033[96mEnter option (compress/convert/removebg) or exit: \033[0m").lower()
    

if option == "convert":
      image_format = input("\033[95mEnter the format to convert to (e.g., JPEG, PNG): \033[0m").lower()
      send_image_and_format(image_path, image_format, server_address, server_port,option)
elif option == "removebg":
        image_format = None
        send_image_and_format(image_path, image_format, server_address, server_port,option)
elif option == "compress":
    root, format = os.path.splitext(image_path)
    image_format = format[1:]
    new_size = input("\033[95mEnter new size to compress to (in KB): \033[0m")
    send_image_and_format(image_path, image_format, server_address, server_port,option,new_size = new_size)
elif option == "exit":
        sys.exit()       
else:
        print("\033[91mInvalid option.\033[91m")
        option = input("\033[96mEnter option (compress/convert/removebg) or exit\033[0m").lower()
    
    
