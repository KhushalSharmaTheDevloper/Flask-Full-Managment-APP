from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML template for the search and update forms
html_template = """
<!doctype html>
<html>
    <head>
        <title>Shop Side</title>
    </head>
    <body>
        <h1>Enter a Number to Search</h1>
        <form method="POST">
            <input type="text" name="search_number" placeholder="Enter numbers here" required>
            <button type="submit" name="action" value="search">Search</button>
        </form>
        
        {% if result %}
            <h2>{{ result }}</h2>
        {% endif %}

        <h1>Update Shipping Status</h1>
        <form method="POST">
            <input type="text" name="update_number" placeholder="Enter number to update" required>
            <select name="status">
                <option value="pending">Pending</option>
                <option value="shipped">Shipped</option>
                <option value="delivered">Delivered</option>
            </select>
            <button type="submit" name="action" value="update">Update Status</button>
        </form>
        
        {% if update_result %}
            <h2>{{ update_result }}</h2>
        {% endif %}
    </body>
</html>
"""


def ensure_default_status(file_name):
    lines = []
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) < 3 or parts[-1] not in ["pending", "shipped", "delivered"]:
                # If the status is missing or invalid, add "pending"
                line = f"{line.strip()} pending\n"
            lines.append(line)

    with open(file_name, 'w') as file:
        file.writelines(lines)

def read_person_data(file_name, search_number):
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split()
            name = parts[0]
            numbers = parts[1:-1]  # Exclude the last item (status)
            status = parts[-1]  # The last item is the status
            
            if search_number in numbers:
                return f"Match found! Name: {name}, Secret Key: {numbers}, Status: {status}"
        
    return "No match found for the entered numbers."

def update_shipping_status(file_name, update_number, new_status):
    lines = []
    updated = False

    # Read and update lines
    with open(file_name, 'r') as file:
        for line in file:
            parts = line.strip().split()
            name = parts[0]
            numbers = parts[1:-1]  # Secret keys
            status = parts[-1]  # Current status
            
            if update_number in numbers:
                # Update the status for the matching entry
                updated_line = f"{name} {' '.join(numbers)} {new_status}\n"
                lines.append(updated_line)
                updated = True
            else:
                lines.append(line)
    
    # Write back to the file with the updated status
    if updated:
        with open(file_name, 'w') as file:
            file.writelines(lines)
        return f"Status updated to '{new_status}' for Secret Key '{update_number}'."
    else:
        return "No match found to update for the entered number."

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    update_result = None

    if request.method == 'POST':
        action = request.form['action']

        if action == "search":
            search_number = request.form['search_number']
            result = read_person_data("user_data.txt", search_number)

        elif action == "update":
            update_number = request.form['update_number']
            new_status = request.form['status']
            update_result = update_shipping_status("user_data.txt", update_number, new_status)

    return render_template_string(html_template, result=result, update_result=update_result)

if __name__ == '__main__':
    # Ensure "pending" is added to any lines missing a status before running the app
    ensure_default_status("user_data.txt")
    app.run(debug=True)
