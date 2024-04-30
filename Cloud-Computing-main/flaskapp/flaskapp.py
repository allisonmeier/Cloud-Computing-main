import os
from flask import Flask, redirect, render_template, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__) # simplify not-so-simple naming conventions
app.config['UPLOAD_FOLDER'] = 'uploads'
user_info = {} # this is where any inputted user info will be temporarily stored at
file_info = {}

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://admin:password@project2-database.cxgsc20owlb0.us-east-2.rds.amazonaws.com:3306/project2-database'
db = SQLAlchemy(app)

class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), unique=True, nullable=False)
    last_name = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return f'User {self.username}'

class FileData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    file_data = db.Column(db.LargeBinary)
    word_count = db.Column(db.Integer)

# ===============================================================
# the most basic landing page
# "/"
@app.route('/')
def index(): # go to home page, using home_page.html
    return render_template('index.html')
# ===============================================================


# ===============================================================
# just the home page
# "/home-page"
@app.route('/home')
def home(): # go to home page, using home_page.html
    return render_template('home_page.html')
# ===============================================================


# ===============================================================
# registration page
# "/registration-page"
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    # first, collect inputted info from registration form
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')

        user = UserData(username=username,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        email=email)
        
        db.session.add(user)
        db.session.commit()
        print('Added user to db: ', user)

        # # then, store inputted info in a dict, given the user's username
        # user_info[username] = {
        #     'password': password,
        #     'first_name': first_name,
        #     'last_name': last_name,
        #     'email': email,
        #     'word_count': 0 # in case there's an error, it's obvious
        # }

        # redirect to go display user info
        link = "http://ec2-18-223-113-204.us-east-2.compute.amazonaws.com/displayuserinfo/" + username
        return redirect(link)

    # assuming GET request, just render general registration page
    return render_template('registration_page.html')

# ===============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    # first, collect inputted info from registration form
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = UserData.query.filter_by(username='john').first()
        if password == user.password:
            link = "http://ec2-18-223-113-204.us-east-2.compute.amazonaws.com/displayuserinfo/" + username
            return redirect(link)

        else:
            print("Incorrect Password. Try Again.")
            return render_template('login.html')
            
    # print("User not found. Try again.")
    return render_template('login.html')



# ===============================================================
# displaying user info page, given username
# "/display-user-info/<USERNAME-GOES-HERE>"
@app.route('/displayuserinfo/<username>')
def display_user_info(username):
    user_data = UserData.query.filter_by(username=username).first()
    # check if user is found
    if user_data:
        # just display it, there's not much to this
        return render_template(
            'display_user_info.html', 
            username=username,
            user_info_to_display=user_data
            )
    else:
        link = "http://ec2-18-223-113-204.us-east-2.compute.amazonaws.com/displayuserinfo/" + username
        return redirect(link)

# ===============================================================


# ===============================================================
# retrieve user info, based on username and password input
# "/retrieve-user-info"
@app.route('/retrieveuserinfo', methods=['POST'])
def retrieve_user_info():
    # collect info from input form
    username = request.form.get('username')
    password = request.form.get('password')

    # check if username and password match
    if user_info.get(username, {}).get('password') == password:
        # they match?
        link = "http://ec2-18-223-113-204.us-east-2.compute.amazonaws.com/displayuserinfo/" + username
        return redirect(link)

    # they don't match?
    return "Username and Password don't match."
# ===============================================================


# ===============================================================
# upload page for text file
# "/upload"
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            file_name = file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
            file.save(file_path)

            # read file contents
            with open(file_path, 'r') as f:
                file_text = f.read()

            # Get word count
            word_count = get_file_wordcount(file_path)

            # Store file text and word count in dictionary
            file_info[file_name] = {
                'text': file_text,
                'word_count': word_count
            }

            return redirect("http://ec2-18-223-113-204.us-east-2.compute.amazonaws.com/upload")

    return render_template('upload.html')

# helper for word count
def get_file_wordcount(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
        word_count = len(text.split())
    return word_count
# ===============================================================


# ===============================================================
# download page for text file, given username
# "/download/<USERNAME-GOES-HERE>"
@app.route('/download/<username>')
def download_file(username, file_name):
    # collect previously stored user info
    current_user = user_info.get(username, {})

    # get path to file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

    if os.path.exists(file_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], file_name, as_attachment=True)
    else:
        return "File not found"
# ===============================================================


# ===============================================================
if __name__ == '__main__':
    app.run(debug=True)
# ===============================================================
