from flask import Flask, render_template, session, request, redirect, url_for, jsonify,flash
import requests
from flask_sqlalchemy import SQLAlchemy
from forms import CarbonFootPrintForm
import joblib
import pandas as pd
import plotly.express as px 
from datetime import datetime
from flask_migrate import Migrate
from flask_login import LoginManager,UserMixin


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.secret_key = '123'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

class User( db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    city = db.Column(db.String(120))
    is_admin = db.Column(db.Boolean, default=False) 


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    likes = db.relationship('Like', backref='post', lazy='dynamic')

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('likes', lazy='dynamic'))

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

class Leaderboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    carbon_emission = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref=db.backref('leaderboard_entries', lazy=True))

with app.app_context():
    db.create_all()
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(
            username="admin", 
            email="admin@example.com", 
            password="123", 
            city="Andhra", 
            is_admin=True 
        )
        db.session.add(admin_user)
        db.session.commit()
    

openWeatherMapApiKey = '0cf7c26dfafe8347249c852c4a0610b1'
aqiApikey = '0dd8f922-0e14-4f03-9ad4-3c7f7697602b'
newsApiKey = 'pub_6108272b24e2c701b3ff651b3474ed577b0b4'

MODEL_PATH = "carbon_footprint_model.pkl"
ENCODERS_PATH = "label_encoders.pkl"
SCALER_PATH = "scaler.pkl"

model  = joblib.load(MODEL_PATH)
label_encoders = joblib.load(ENCODERS_PATH)
scaler = joblib.load(SCALER_PATH)

historical_data = pd.DataFrame(columns=['Date','Carbon Emission'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    username_error = None
    password_error = None
    invalid_credentials_error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username:
            username_error = "Please enter username"
        if not password:
            password_error = "Please enter password"
        else:
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                session['user_id'] = user.id
                session['is_admin'] = user.is_admin
                return redirect(url_for('home'))
            else:
                invalid_credentials_error = "Invalid username or password."
    return render_template('login.html', username_error=username_error,password_error=password_error,invalid_credentials_error=invalid_credentials_error)


@app.route('/register', methods=['GET', 'POST'])
def register():
    username_error = None
    email_error = None
    password_error = None
    city_error = None
    already_exists_error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        city = request.form.get('city')
        if not username: 
            username_error = "Please enter username"
        if not email:
            email_error = "Please enter email"
        if not password:
            password_error = "Please enter password"
        if not city:
            city_error = "Please enter city"
        if not username_error and not email_error and not password_error and not city_error:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                already_exists_error = "Username already taken."
            else:
                new_user = User(username=username, email=email, password=password, city=city)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for('login'))
    return render_template('register.html', username_error=username_error,email_error=email_error,password_error=password_error,city_error=city_error,already_exists_error=already_exists_error)


@app.route('/welcome')
def welcome():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('welcome.html')


@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')


@app.route('/community', methods=["GET", "POST"])
def community():
    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('user_id')
        new_post = Post(title=title, content=content, author_id=user_id)
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('community'))
    if 'is_admin' in session and session['is_admin']:
        posts = Post.query.all() 
    else:
        posts = Post.query.all()
    return render_template('community.html', posts=posts)


@app.route('/post/<int:post_id>', methods=["GET", "POST"])
def post(post_id):
    post = Post.query.get_or_404(post_id)
    user_id = session.get('user_id') 
    if not user_id:
        return redirect(url_for('login'))
    if request.method == "POST":
        if 'like' in request.form:
            existing_like = Like.query.filter_by(post_id=post.id, user_id=user_id).first()
            if existing_like:
                db.session.delete(existing_like)
            else:
                new_like = Like(post_id=post.id, user_id=user_id)
                db.session.add(new_like)
            db.session.commit()
        else:
            content = request.form['content']
            new_comment = Comment(content=content, post_id=post_id, author_id=user_id)
            db.session.add(new_comment)
            db.session.commit()
    user_likes = Like.query.filter_by(post_id=post.id, user_id=user_id).all()
    likes_count = len(user_likes) 
    user_has_liked = len(user_likes) > 0 
    all_likes_count = post.likes.count() 

    return render_template('post.html', post=post, likes_count=all_likes_count, 
                           user_has_liked=user_has_liked)

@app.route('/admin/delete_post/<int:post_id>')
@app.route('/admin/delete_post/<int:post_id>')
def delete_post(post_id):
    post = Post.query.get(post_id)
    if post:
        likes = Like.query.filter_by(post_id=post.id).all()
        for like in likes:
            db.session.delete(like)
        for comment in post.comments:
            db.session.delete(comment)

        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('community'))
    else:
        return redirect(url_for('error_page'))

@app.route('/admin/delete_comment/<int:comment_id>')
def delete_comment(comment_id):
    if 'is_admin' not in session or not session['is_admin']:
        return redirect(url_for('home'))  
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('post', post_id=comment.post_id))


@app.route('/form', methods=['GET', 'POST'])
def form():
    form = CarbonFootPrintForm()  
    if form.validate_on_submit(): 
        input_data = {
            'Body Type':form.body_type.data,
            'Sex':form.sex.data,
            'Diet':form.diet.data,
            'How Often Shower':form.shower.data,
            'Heating Energy Source':form.heating_energy_source.data,
            'Transport':form.transport.data,
            'Vehicle Type':form.vehicle_type.data,
            'Social Activity':form.social_activity.data,
            'Monthly Grocery Bill':form.grocery_bill.data,
            'Frequency of Traveling by Air':form.air_travel.data,
            'Vehicle Monthly Distance Km':form.vehicle_distance.data,
            'Waste Bag Size':form.waste_bag_size.data,
            'Waste Bag Weekly Count':form.waste_bag_count.data,
            'How Long TV PC Daily Hour':form.tv_pc_hours.data,
            'How Many New Clothes Monthly':form.new_clothes.data,
            'How Long Internet Daily Hour':form.internet_hours.data,
            'Energy efficiency':form.energy_efficiency.data,
        }
        df = pd.DataFrame([input_data])
        mappings={
            'Social Activity':{'often':3,'sometimes':2,'rarely':1,'never':0},
            'Frequency of Traveling by Air':{'very frequently':4,'frequently':3,'rarely':2,'never':1},
            'Waste Bag Size':{'small':1,'medium':2,'large':3,'extra large':4},
            'Energy efficiency':{'No':0,'Sometimes':1,'Yes':2},
        }
        for column,mapping in mappings.items():
            if column in df.columns:
                df[column]=df[column].map(mapping)
        categorical_columns = ['Body Type','Sex','Diet','Transport','Vehicle Type','How Often Shower','Heating Energy Source']
        for col in categorical_columns:
            if col in label_encoders:
                df[col]=label_encoders[col].transform(df[col].astype(str))
        numerical_columns = ['Monthly Grocery Bill','Vehicle Monthly Distance Km','Waste Bag Weekly Count',
                         'How Long TV PC Daily Hour','How Many New Clothes Monthly','How Long Internet Daily Hour']
        df[numerical_columns]=scaler.transform(df[numerical_columns])
        prediction = model.predict(df)[0]
    
        global historical_data
        historical_data=pd.concat(
            [historical_data,pd.DataFrame({'Date':[pd.Timestamp.now()],'Carbon Emission':[prediction]})],
            ignore_index=True
        )
        return redirect(url_for('result',emission=prediction))
    return render_template('form.html', form=form) 
 

@app.route('/result', methods=['GET', 'POST'])
def result():
    emission = request.args.get('emission', None)
    if emission:  
        emission = float(emission)  
    else:
        emission = 0.0  
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            leaderboard_entry = Leaderboard(user_id=user.id, carbon_emission=emission)
            db.session.add(leaderboard_entry)
            db.session.commit()
        else:
            print(f"Error: User ID {session['user_id']} does not exist in the database.")
            flash("Error: User not found. Could not save emission.", "error")
    else:
        print("Error: No user ID in session.")
        flash("Error: You must be logged in to save your results.", "error")
    return render_template('result.html', emission=emission)


@app.route('/leaderboard')
def leaderboard():
    leaderboard_query = db.session.query(
        Leaderboard.user_id, db.func.avg(Leaderboard.carbon_emission).label('avg_emission')
    ).join(User, User.id == Leaderboard.user_id).group_by(Leaderboard.user_id).order_by(db.func.avg(Leaderboard.carbon_emission).asc()).all()
    leaderboard = []
    for idx, (user_id, avg_emission) in enumerate(leaderboard_query):
        user = User.query.get(user_id)
        if user:
            name = session.get('username', user.username if user.username else "Anonymous")
            city = session.get('city', user.city if user.city else "Unknown")
            leaderboard.append({
                "rank": idx + 1,
                "name": name,
                "city": city,
                "carbon_emission": round(avg_emission, 2),  
            })
    return render_template('leaderboard.html', leaderboard=leaderboard)


@app.route('/visualize')
def visualize():
    if 'user_id' not in session:
        flash("You need to be logged in to view your emission history.", "error")
        return redirect(url_for('login'))
    user_id = session['user_id']
    historical_data = Leaderboard.query.filter_by(user_id=user_id).order_by(Leaderboard.date_recorded).all()
    if not historical_data:
        return "No data available for Visualization!"
    data = {
        'Date': [entry.date_recorded for entry in historical_data], 
        'Carbon Emission': [entry.carbon_emission for entry in historical_data] 
    }
    df = pd.DataFrame(data)
    fig = px.line(df, x='Date', y='Carbon Emission', title='Carbon Emission Trends Over Time')
    fig_html = fig.to_html(full_html=False)
    return render_template('visualize.html', plot_html=fig_html)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/api/weather', methods=['GET'])
def api_weather():
    city = request.args.get('city', 'Bhimavaram')
    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={openWeatherMapApiKey}&units=metric"
    weather_response = requests.get(weather_url)
    if weather_response.status_code != 200:
        return jsonify({'error': 'Could not fetch weather data'}), 500
    weather_data = weather_response.json()
    try:
        aqi_url = f"https://api.waqi.info/feed/{city}/?token=132f67be1b7c0decb2f2135bafb77d0f692bec9a"
        aqi_response = requests.get(aqi_url)
        aqi_json = aqi_response.json()
        if aqi_json.get('status') == "ok":
            aqi_data = aqi_json.get('data', {})
            aqi = aqi_data.get('aqi', 'N/A')
            if aqi != 'N/A':
                if aqi <= 50:
                    aqi_status = "Good"
                elif aqi <= 100:
                    aqi_status = "Moderate"
                elif aqi <= 150:
                    aqi_status = "Unhealthy for Sensitive Groups"
                elif aqi <= 200:
                    aqi_status = "Unhealthy"
                elif aqi <= 300:
                    aqi_status = "Very Unhealthy"
                else:
                    aqi_status = "Hazardous"
            else:
                aqi_status = "N/A"
        else:
            print(f"Error: {aqi_json.get('data', 'Unknown error')}")
            aqi_status = "N/A"
    except Exception as e:
        aqi_status = "N/A"
        print(f"Error fetching AQI: {e}")
    weather_data['aqi_status'] = aqi_status
    return jsonify(weather_data)


@app.route('/api/news')
def get_news():
    city = request.args.get('city')
    if not city:
        return jsonify({"error": "City is required"}), 400
    url = f"https://newsdata.io/api/1/latest?apikey=pub_606934e17c47151f23ec0bc338d60f08a5e31&q={city}"
    response = requests.get(url)
    news_data = response.json()
    if response.status_code == 200:
        return jsonify(news_data)
    else:
        return jsonify({"error": "Failed to fetch news"}), 500


if __name__ == '__main__':
    app.run(debug=True)
