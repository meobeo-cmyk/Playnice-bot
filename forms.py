from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class AddKeywordForm(FlaskForm):
    keyword = StringField('Từ khóa', validators=[DataRequired(), Length(min=1, max=200)])
    category = SelectField('Loại vi phạm', choices=[
        ('PROFANITY', 'Ngôn từ thô tục'),
        ('HARASSMENT', 'Quấy rối, gạ gẫm'),
        ('OFFENSIVE', 'Nội dung xúc phạm'),
        ('SPAM', 'Spam')
    ], validators=[DataRequired()])
    context = TextAreaField('Ngữ cảnh sử dụng', validators=[Length(max=500)])
    severity = SelectField('Mức độ nghiêm trọng', choices=[
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao')
    ], default='medium')
    is_active = BooleanField('Kích hoạt', default=True)
    submit = SubmitField('Thêm từ khóa')

class EditKeywordForm(FlaskForm):
    keyword = StringField('Từ khóa', validators=[DataRequired(), Length(min=1, max=200)])
    category = SelectField('Loại vi phạm', choices=[
        ('PROFANITY', 'Ngôn từ thô tục'),
        ('HARASSMENT', 'Quấy rối, gạ gẫm'),
        ('OFFENSIVE', 'Nội dung xúc phạm'),
        ('SPAM', 'Spam')
    ], validators=[DataRequired()])
    context = TextAreaField('Ngữ cảnh sử dụng', validators=[Length(max=500)])
    severity = SelectField('Mức độ nghiêm trọng', choices=[
        ('low', 'Thấp'),
        ('medium', 'Trung bình'),
        ('high', 'Cao')
    ])
    is_active = BooleanField('Kích hoạt')
    submit = SubmitField('Cập nhật')

class BotSettingsForm(FlaskForm):
    mute_duration = StringField('Thời gian mute (phút)', validators=[DataRequired()])
    invite_mute_duration = StringField('Thời gian mute link Discord (phút)', validators=[DataRequired()])
    ai_moderation = BooleanField('Sử dụng AI kiểm duyệt')
    submit = SubmitField('Lưu cài đặt')