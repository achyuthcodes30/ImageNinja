import socket
import threading
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
from io import BytesIO
import ssl
import rembg



def convert_image(image_format, image_data):
    img = Image.open(BytesIO(image_data))
    output_buffer = BytesIO()
    img = img.convert("RGB")
    image_format = image_format.lower()
    img.save(output_buffer, format=image_format)
    output_buffer.seek(0)
    converted_image = output_buffer.getvalue()
    return converted_image
    
def remove_bg(image_data):
    input_image = Image.open(BytesIO(image_data))
    output_image = rembg.remove(input_image)
    output_buffer = BytesIO()
    output_image.save(output_buffer, format="PNG")
    output_image_data = output_buffer.getvalue()
    return output_image_data
    
def compress_image(image_format,image_data, target_size_kb):
    quality = 95  
   
    img = Image.open(BytesIO(image_data))
    
    while True:
        resized_img = img.resize((int(img.width * 0.95), int(img.height * 0.95)))
        output_buffer = BytesIO()
        resized_img.save(output_buffer, format=image_format,optimize=True, quality=quality)
        compressed_image = output_buffer.getvalue()
        if len(compressed_image) <= int(target_size_kb) * 1024:
            return compressed_image  
        quality -= 5
        img = resized_img
        
         
        
def handle_client(client_socket):
    try:
        
        image_size = int.from_bytes(client_socket.recv(4), byteorder='big')
        
        
        image_data = b''
        while len(image_data) < image_size:
            chunk = client_socket.recv(4096)
            
            if not chunk:
                
                break
            image_data += chunk
        
        client_socket.sendall(b'ACK')
        option = client_socket.recv(1024).decode()
        if not option:
            print("Error receiving option")
        else:
            client_socket.sendall(b'ACK')
            
            if option == "convert":
             image_format = client_socket.recv(4096).decode()
             
        
             converted_image = convert_image(image_format,image_data)
             client_socket.sendall(converted_image)
            elif option == "removebg":
                new_image = remove_bg(image_data)
                client_socket.sendall(new_image)
            else:
                image_format = client_socket.recv(4096).decode()
                client_socket.sendall(b'ACK')
                new_size = client_socket.recv(4096).decode()
                compressed_image = compress_image(image_format,image_data,new_size)
                if(compressed_image):
                    client_socket.sendall(compressed_image)
                    
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        client_socket.close()


def socket_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('0.0.0.0', port)
    server_socket.bind(server_address)
    server_socket.listen()
    
    print("Socket server is listening...")
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile='server.crt', keyfile='server.key')
    max_connections = 200
    with ThreadPoolExecutor(max_workers=max_connections) as executor:
    
     while True:
         client_socket, client_address = server_socket.accept()
         print("Connection from", client_address)
         ssl_socket = ssl_context.wrap_socket(client_socket, server_side=True)
         executor.submit(handle_client, ssl_socket)
        

if __name__ == "__main__":
  socket_server(8888)


