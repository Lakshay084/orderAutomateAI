from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import os
import pandas as pd
from services.gemini_service import GeminiClient
from services.email_service import send_email
import sqlite3
from datetime import datetime
from services.email_parser import EmailParser


app = Flask(__name__)
CORS(app)

gemini_client = GeminiClient()
load_dotenv()
# # client = os.getenv("OPENAI_API_KEY")
# client = OpenAI(
#     api_key=os.getenv("OPENAI_API_KEY")  )

# openai.api_key = "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"
# Configure the upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'data')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Root route
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the OrderAutomateAI API!"})

# File upload route
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return jsonify({"message": "File uploaded successfully!", "file_path": file_path}), 200


@app.route('/process-file', methods=['POST'])
def process_file():
    try:
        # Get the file path from the request
        print("Request received:", request.json)
        file_path = request.json.get("file_path")
        print("Received file path:", file_path)
        if not file_path or not os.path.exists(file_path):
            print("Invalid file path or file does not exist")
            return jsonify({"error": "Invalid file path"}), 400

        # Load the CSV file into a pandas DataFrame
        data = pd.read_csv(file_path)
        print("Data loaded successfully:", data.head())

        # Perform basic analysis
        total_suppliers = data["Supplier ID"].nunique()  # Count unique suppliers
        pending_orders = data[data["Order Status"] == "Pending"].shape[0]  # Count pending orders
        avg_price_per_unit = data["Price per Unit"].mean()  # Calculate average price

        best_supplier = data.sort_values(by=['Rating', 'Price per Unit'], ascending=[False, True]).iloc[0]

        best_supplier_info = {
            "Supplier ID": best_supplier['Supplier ID'],
            "Supplier Name": best_supplier["Supplier Name"],
            "Rating": best_supplier["Rating"],
            "Price per Unit": best_supplier["Price per Unit"]
        }

        # Identify suppliers for renegotiation
        renegotiation_candidates = data[(data["Rating"] < 3.5) & (data["Price per Unit"] > avg_price_per_unit)]
        renegotiation_list = renegotiation_candidates[["Supplier ID", "Supplier Name", "Rating", "Price per Unit"]].to_dict(orient="records")

        restocking_candidates = data[data["Quantity Ordered"] < 200]
        restocking_list = restocking_candidates[["Supplier ID", "Supplier Name", "Quantity Ordered"]].to_dict(orient="records")


        # Return analysis as a JSON response
        return jsonify({
            "message": "File processed successfully!",
            "total_suppliers": total_suppliers,
            "pending_orders": pending_orders,
            "average_price_per_unit": round(avg_price_per_unit, 2),
            "best_supplier": best_supplier_info,
            "renegotiation_candidates": renegotiation_list,
            "restocking_alerts": restocking_list,
        }), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/generate-email', methods=['POST'])
def generate_email():
    try:
        # Get supplier details from the request
        data = request.json
        supplier_name = data.get("supplier_name", "Supplier")
        purpose = data.get("purpose", "negotiation")
        product_name = data.get("product_name", "your product")
        price = data.get("price_per_unit", "N/A")
        rating = data.get("rating", "N/A")

        # Generate email using GeminiClient
        email_content = gemini_client.generate_email(supplier_name, purpose, product_name, price, rating)

        return jsonify({"message": "Email draft generated successfully!", "email_draft": email_content}), 200
    except Exception as e:
        # Enhanced error message for debugging
        print("Error in generate_email:", str(e))
        return jsonify({"error": str(e)}), 500
    

@app.route('/send-email', methods=['POST'])
def send_email_endpoint():
    try:
        # Get request data
        data = request.json
        to_email = data.get("to_email", "recipient@example.com")
        supplier_name = data.get("Supplier Name")
        purpose = data.get("Purpose")
        product_name = data.get("Product Name")
        price = data.get("Price per Unit")
        rating = data.get("Rating")

        # Generate email draft using Gemini
        email_body = gemini_client.generate_email(
            supplier_name, purpose, product_name, price, rating
        )
        subject = f"Email to {supplier_name} - Purpose: {purpose}"

        # Send the email
        result = send_email(to_email, subject, email_body)

        return jsonify({"message": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/suppliers/<product>', methods=['GET'])
def get_suppliers_by_product(product):
    try:
        # Connect to the database
        conn = sqlite3.connect('./database/database.db', check_same_thread=False)
        cursor = conn.cursor()

        # Query suppliers for the given product
        query = "SELECT name, email, product, price_per_unit, quantity_available, agreement_status FROM suppliers WHERE product = ?"
        cursor.execute(query, (product,))
        suppliers = cursor.fetchall()

        # Structure the response
        supplier_data = [
            {
                "name": row[0],
                "email": row[1],
                "product": row[2],
                "price_per_unit": row[3],
                "quantity_available": row[4],
                "agreement_status": row[5],
            }
            for row in suppliers
        ]

        conn.close()

        return jsonify({"suppliers": supplier_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    
admin_requirements = {}

@app.route('/set-requirements/<product>', methods=['POST'])
def set_requirements(product):
    global admin_requirements
    try:
        data = request.json
        admin_requirements[product] = data
        return jsonify({"message": f"{product} requirements updated successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500   

@app.route('/filtered-suppliers/<product>', methods=['GET'])
def get_filtered_suppliers(product):
    try:
        global admin_requirements

        # Check if requirements for the product exist
        if product not in admin_requirements:
            return jsonify({"error": f"No requirements set for {product}."}), 400

        # Get the admin-defined requirements for the product
        requirements = admin_requirements[product]
        max_price = requirements["max_price"]
        min_rating = requirements["min_rating"]
        required_quantity = requirements["required_quantity"]

        # Connect to the database
        conn = sqlite3.connect('./database/database.db', check_same_thread=False)
        cursor = conn.cursor()
        today_date = datetime.now().strftime('%Y-%m-%d')

        # Query suppliers based on requirements
        query = """
            SELECT name, email, product, price_per_unit, quantity_available, rating, agreement_status, date_created
            FROM suppliers
            WHERE product = ?
            AND price_per_unit <= ?
            AND rating >= ?
            AND quantity_available >= ?
            AND date(date_created) = ?
        """
        cursor.execute(query, (product, max_price, min_rating, required_quantity, today_date))
        suppliers = cursor.fetchall()

        # Structure the response
        supplier_data = [
            {
                "name": row[0],
                "email": row[1],
                "product": row[2],
                "price_per_unit": row[3],
                "quantity_available": row[4],
                "rating": row[5],
                "agreement_status": row[6],
                "date_created": row[7],
            }
            for row in suppliers
        ]

        conn.close()

        return jsonify({"suppliers": supplier_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/send-negotiation-emails', methods=['POST'])
def send_negotiation_emails():
    try:
        global admin_requirements

        # Get admin requirements from the global variable
        if not admin_requirements:
            return jsonify({"error": "Admin requirements are not set."}), 400

        # Connect to the database
        conn = sqlite3.connect('./database/database.db', check_same_thread=False)
        cursor = conn.cursor()

        # Loop through products and send emails to non-compliant suppliers
        for product, requirements in admin_requirements.items():
            max_price = requirements["max_price"]
            min_rating = requirements["min_rating"]
            required_quantity = requirements["required_quantity"]

            # Query suppliers who do not meet the requirements
            query = """
                SELECT id, name, email, product, price_per_unit, quantity_available, rating
                FROM suppliers
                WHERE product = ?
                AND (price_per_unit > ? OR rating < ? OR quantity_available < ?)
            """
            cursor.execute(query, (product, max_price, min_rating, required_quantity))
            suppliers_to_email = cursor.fetchall()

            # Send negotiation emails
            for supplier in suppliers_to_email:
                supplier_id, name, email, product, price, quantity, rating = supplier
                gemini_client = GeminiClient()
                email_content = gemini_client.generate_email(
                    supplier_name=name,
                    purpose="negotiation",
                    product_name=product,
                    price=price,
                    rating=rating,
                )

                # Log the communication in the database
                cursor.execute(
                    """
                    INSERT INTO communications (supplier_id, email_subject, email_body, email_status)
                    VALUES (?, ?, ?, ?)
                    """,
                    (supplier_id, f"Negotiation for {product}", email_content, "Sent"),
                )

                # Debugging/logging
                print(f"Email sent to {email}: {email_content}")

        conn.commit()
        conn.close()

        return jsonify({"message": "Negotiation emails sent successfully!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/process-supplier-email', methods=['POST'])
def process_supplier_email():
    try:
        email_content = request.json.get("email_content")
        if not email_content:
            return jsonify({"error": "No email content provided"}), 400

        # Parse the email content
        parsed_data = EmailParser.parse_email(email_content)

        supplier_name = parsed_data["supplier_name"]
        agreed_price = parsed_data["agreed_price"] or 0.0  # Default to 0.0 if missing
        quantity = parsed_data["quantity"] or 0           # Default to 0 if missing
        status = parsed_data["status"]

        if not parsed_data["supplier_name"]:
            return jsonify({"error": "Could not parse supplier name from email"}), 400

        # Update the database with the parsed details
        conn = sqlite3.connect('./database/database.db', check_same_thread=False)
        cursor = conn.cursor()

        query = """
            UPDATE suppliers
            SET price_per_unit = ?, quantity_available = ?, agreement_status = ?
            WHERE name = ?
        """
        cursor.execute(
            query,
            (agreed_price, quantity, status, supplier_name),
        )

        conn.commit()
        conn.close()

        return jsonify({"message": "Supplier details updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
