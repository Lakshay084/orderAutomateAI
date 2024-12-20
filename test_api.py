# import requests

# # API URL
# url = "http://127.0.0.1:5000/generate-email"

# # Corrected Payload
# payload = {
#     "supplier_name": "Supplier_3",
#     "purpose": "negotiation",
#     "product_name": "Wheat",
#     "price_per_unit": 368,
#     "rating": 3.4
# }

# # Debugging: Print payload
# print("Sending payload:", payload)

# # Send the POST request
# response = requests.post(url, json=payload)

# # Print response status and text
# print("Status Code:", response.status_code)
# print("Response Text:", response.text)

# # Parse and print JSON response if available
# try:
#     print(response.json())
# except Exception as e:
#     print("Error parsing JSON:", str(e))


import requests

url = "http://127.0.0.1:5000/send-email"

payload = {
    "to_email": "recipient-email@gmail.com",
    "Supplier Name": "Supplier_3",
    "Purpose": "negotiation",
    "Product Name": "Wheat",
    "Price per Unit": 368,
    "Rating": 3.4
}

response = requests.post(url, json=payload)

print("Status Code:", response.status_code)
print("Response Text:", response.text)
