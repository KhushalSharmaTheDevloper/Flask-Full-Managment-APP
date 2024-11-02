from flask import Flask, render_template, request, redirect, url_for, flash
import random
import time
import subprocess

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # required for flashing messages

# Notification function (macOS-specific)
def send_notification(title, message):
    script = f'display notification "{message}" with title "{title}"'
    subprocess.run(["osascript", "-e", script])

def ensure_default_status(file_name):
    lines = []
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) < 4 or parts[-1] not in ["pending", "shipped", "delivered"]:
                # If the status is missing or invalid, add "pending"
                line = f"{line.strip()} pending\n"
            lines.append(line)

    with open(file_name, 'w') as file:
        file.writelines(lines)

# Homepage with confirmation form
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = request.form.get("username")
        quantity_str = request.form.get("quantity")  # Get the quantity as a string

        # Check if the quantity is provided and is a valid integer
        if quantity_str is not None and quantity_str.isdigit():
            quantity = int(quantity_str)  # Convert to int
            price = quantity * 97  # Calculate the price
            
            if request.form.get("confirm") == "yes":
                # Simulate processing time
                time.sleep(2)
                # Generate the purchase key
                key = random.randint(20000525929592592250, 999999491949194929499592952925225252)

                # Save data to file with default status "pending"
                with open("user_data.txt", "a") as file:
                    file.write(f"{user} {key} {quantity} pending\n")
                    
                # Send notification
                send_notification(f"{user} bought {quantity}", " of Our product | KEY GENERATED |")

                flash("Your purchase was successful! Key generated.", "success")
                return redirect(url_for('confirmation'))
        else:
            flash("Please enter a valid quantity.", "error")  # Flash an error message

    return render_template('index.html')

# Confirmation page route
@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

# Route to check the status of a number
@app.route('/check_status', methods=['GET', 'POST'])
def check_status():
    result = None
    if request.method == 'POST':
        search_number = request.form.get("search_number")
        if search_number:
            result = get_status_from_file("user_data.txt", search_number)
        else:
            flash("Please enter a valid number.", "error")
    
    return render_template('check_status.html', result=result)

def get_status_from_file(file_name, search_number):
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) >= 3 and parts[1] == search_number:  # Assuming the number is the second part
                return f"Status for {search_number}: {parts[-1]}"  # Return the last part as status
    return "No match found for the entered number."

if __name__ == "__main__":
    # Ensure "pending" is added to any lines missing a status before running the app
    ensure_default_status("user_data.txt")
    app.run(host="0.0.0.0", port=5000, debug=True)
    