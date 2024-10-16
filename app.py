from flask import Flask, render_template, request, redirect, url_for, flash
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management

# Replace with your Webex API base URL
WEBEX_API_URL = "https://webexapis.com/v1"

# Route for the main page to enter the Webex token
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        access_token = request.form['access_token']
        headers = {'Authorization': f'Bearer {access_token}'}
        user_info = requests.get(f'{WEBEX_API_URL}/people/me', headers=headers).json()
        if 'errors' in user_info:
            return "Invalid Token. Please try again."
        else:
            return redirect(url_for('menu', access_token=access_token))
    return render_template('index.html')

# Route for the main menu with options
@app.route('/menu/<access_token>', methods=['GET'])
def menu(access_token):
    return render_template('menu.html', access_token=access_token)

# Route to test connection
@app.route('/test_connection/<access_token>')
def test_connection(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{WEBEX_API_URL}/people/me", headers=headers)

    if response.status_code == 200:
        flash("Connection successful!", "success")
    else:
        flash("Connection failed! Check your token.", "error")

    return redirect(url_for('menu', access_token=access_token))

# Route to display user information
@app.route('/user_info/<access_token>')
def user_info(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(f"{WEBEX_API_URL}/people/me", headers=headers)

    if response.status_code == 200:
        user_info = response.json()
        return render_template('user_info.html', user_info=user_info, access_token=access_token)
    else:
        flash("Failed to retrieve user info.", "error")
        return redirect(url_for('menu', access_token=access_token))

# Route to list rooms and send messages
@app.route('/rooms/<access_token>', methods=['GET', 'POST'])
def rooms(access_token):
    headers = {'Authorization': f'Bearer {access_token}'}

    # Fetch rooms
    rooms_data = requests.get(f'{WEBEX_API_URL}/rooms', headers=headers).json()

    # Display rooms for selection
    return render_template('rooms.html', rooms=rooms_data['items'], access_token=access_token)

# Route to send a message to a selected room
@app.route('/send_message/<access_token>', methods=['POST'])
def send_message(access_token):
    room_id = request.form['room_id']
    message = request.form['message']
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(f"{WEBEX_API_URL}/messages", headers=headers, json={
        "roomId": room_id,
        "text": message
    })

    if response.status_code == 200:
        flash("Message sent successfully!", "success")
    else:
        flash("Failed to send message.", "error")

    return redirect(url_for('rooms', access_token=access_token))

# Route to create a new room
@app.route('/create_room/<access_token>', methods=['GET', 'POST'])
def create_room(access_token):
    if request.method == 'POST':
        title = request.form['title']
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.post(f"{WEBEX_API_URL}/rooms", headers=headers, json={"title": title})

        if response.status_code == 200:
            flash("Room created successfully!", "success")
        else:
            flash("Failed to create room.", "error")

        return redirect(url_for('menu', access_token=access_token))

    return render_template('create_room.html', access_token=access_token)

if __name__ == '__main__':
    app.run(debug=True)
