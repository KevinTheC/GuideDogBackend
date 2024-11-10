# import requests

# # Function to send the image
# def send_image(image_path, server_url):
#     # Open the image file in binary mode
#     with open(image_path, 'rb') as image_file:
#         files = {'image': image_file}
        
#         # Send the POST request to the server with the image
#         response = requests.post(server_url, files=files)
        
#         # Check if the request was successful
#         if response.status_code == 200:
#             print("Image sent successfully.")
#         else:
#             print("Failed to send image. Server responded with:", response.status_code)
#         try:
#             json_response = response.json()  # Parse the response as JSON
#             print("Server JSON Response:", json_response)
#         except ValueError:
#             print("Error: Response is not valid JSON.")

# # Example usage
# if __name__ == "__main__":
#     image_path = '20241109_171354.jpg'  # Change this to the path of your image
#     server_url = 'http://127.0.0.1:443/process_image'  # Local server URL and port
    
#     send_image(image_path, server_url)
