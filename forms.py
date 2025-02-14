from flask_wtf import FlaskForm 
from wtforms import StringField,SelectField,FloatField,SubmitField,IntegerField 
from wtforms.validators import DataRequired 
from wtforms import PasswordField,BooleanField 
from wtforms.validators import DataRequired,Email,EqualTo 

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired()])
    submit = SubmitField('Sign Up')
class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
class CarbonFootPrintForm(FlaskForm):
    body_type = StringField('Body Type', validators=[DataRequired()], render_kw={"class": "form-control"})
    sex = StringField('Sex', validators=[DataRequired()], render_kw={"class": "form-control"})
    diet = StringField('Diet', validators=[DataRequired()], render_kw={"class": "form-control"})
    shower = IntegerField('How Often Shower (days)', validators=[DataRequired()], render_kw={"class": "form-control"})
    heating_energy_source = StringField('Heating Energy Source', validators=[DataRequired()], render_kw={"class": "form-control"})
    transport = StringField('Transport', validators=[DataRequired()], render_kw={"class": "form-control"})
    vehicle_type = StringField('Vehicle Type', validators=[DataRequired()], render_kw={"class": "form-control"})
    social_activity = SelectField(
        'Social Activity',
        choices=[('often', 'Often'), ('sometimes', 'Sometimes'), ('rarely', 'Rarely'), ('never', 'Never')],
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    grocery_bill = FloatField('Monthly Grocery Bill', validators=[DataRequired()], render_kw={"class": "form-control"})
    air_travel = SelectField(
        'Frequency of Traveling by Air',
        choices=[('very frequently', 'Very Frequently'), ('frequently', 'Frequently'), ('rarely', 'Rarely'), ('never', 'Never')],
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    vehicle_distance = FloatField('Vehicle Monthly Distance (KM)', validators=[DataRequired()], render_kw={"class": "form-control"})
    waste_bag_size = SelectField(
        'Waste Bag Size',
        choices=[('small', 'Small'), ('medium', 'Medium'), ('large', 'Large'), ('extra large', 'Extra Large')],
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    waste_bag_count = FloatField('Waste Bag Weekly Count', validators=[DataRequired()], render_kw={"class": "form-control"})
    tv_pc_hours = FloatField('How Long TV/PC Daily (hours)', validators=[DataRequired()], render_kw={"class": "form-control"})
    new_clothes = FloatField('How Many New Clothes Monthly', validators=[DataRequired()], render_kw={"class": "form-control"})
    internet_hours = FloatField('How Long Internet Daily (hours)', validators=[DataRequired()], render_kw={"class": "form-control"})
    energy_efficiency = SelectField(
        'Energy Efficiency',
        choices=[('No', 'No'), ('Sometimes', 'Sometimes'), ('Yes', 'Yes')],
        validators=[DataRequired()],
        render_kw={"class": "form-control"}
    )
    submit = SubmitField('Predict', render_kw={"class": "btn-submit"})