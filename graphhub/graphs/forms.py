from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired


class GraphForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    tags = StringField('Tags')
    description = TextAreaField('Description', validators=[DataRequired()])
    project_file = FileField('Project file', validators=[FileAllowed(['gmom']), DataRequired()])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    text = TextAreaField('Add your comment', validators=[DataRequired()])
    submit = SubmitField('Comment')
