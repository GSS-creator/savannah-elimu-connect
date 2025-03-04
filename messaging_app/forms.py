from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, MultipleFileField
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=64)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    terms_accept = BooleanField('I accept the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_phone(self, phone):
        if not phone.data.replace('+', '').replace('-', '').replace(' ', '').isdigit():
            raise ValidationError('Please enter a valid phone number.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Length(max=64)])
    last_name = StringField('Last Name', validators=[Length(max=64)])
    bio = TextAreaField('Bio', validators=[Length(max=500)])
    location = StringField('Location', validators=[Length(max=64)])
    submit = SubmitField('Save Changes')

    def __init__(self, *args, **kwargs):
        self.original_username = kwargs.pop('original_username', None)
        super(EditProfileForm, self).__init__(*args, **kwargs)

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class CreateGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[Length(max=140)])
    submit = SubmitField('Create Group')

class PostForm(FlaskForm):
    content = TextAreaField('Say something...', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Post')

class ProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    location = StringField('Location', validators=[Length(max=100)])
    condition = SelectField('Condition', choices=[
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('used', 'Used')
    ])
    images = MultipleFileField('Product Images', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')
    ])
    category = SelectField('Category', choices=[
        ('electronics', 'Electronics'),
        ('books', 'Books'),
        ('fashion', 'Fashion'),
        ('home', 'Home & Living'),
        ('services', 'Services'),
        ('other', 'Other')
    ])
    submit = SubmitField('Create Listing')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        ('5', '★★★★★ Excellent'),
        ('4', '★★★★ Very Good'),
        ('3', '★★★ Good'),
        ('2', '★★ Fair'),
        ('1', '★ Poor')
    ])
    comment = TextAreaField('Comment', validators=[DataRequired(), Length(max=500)])
    submit = SubmitField('Submit Review')
