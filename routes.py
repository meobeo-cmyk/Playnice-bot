from flask import render_template, request, flash, redirect, url_for, jsonify
from app import app, db
from models import FilterKeyword, ViolationLog, BotSettings
from forms import AddKeywordForm, EditKeywordForm, BotSettingsForm
from datetime import datetime, timedelta
import json

@app.route('/')
def dashboard():
    """Dashboard chính với thống kê tổng quan"""
    # Thống kê vi phạm 7 ngày qua
    week_ago = datetime.utcnow() - timedelta(days=7)
    violations_week = ViolationLog.query.filter(ViolationLog.timestamp >= week_ago).all()
    
    # Thống kê từ khóa
    total_keywords = FilterKeyword.query.filter_by(is_active=True).count()
    
    # Thống kê theo loại vi phạm
    violation_stats = {}
    for violation in violations_week:
        vtype = violation.violation_type
        if vtype not in violation_stats:
            violation_stats[vtype] = 0
        violation_stats[vtype] += 1
    
    # Top vi phạm
    user_violations = {}
    for violation in violations_week:
        user_id = violation.user_id
        if user_id not in user_violations:
            user_violations[user_id] = {
                'username': violation.username,
                'count': 0
            }
        user_violations[user_id]['count'] += 1
    
    top_violators = sorted(user_violations.items(), key=lambda x: x[1]['count'], reverse=True)[:5]
    
    return render_template('dashboard.html',
                         total_violations=len(violations_week),
                         total_keywords=total_keywords,
                         violation_stats=violation_stats,
                         top_violators=top_violators)

@app.route('/keywords')
def keywords():
    """Trang quản lý từ khóa"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = FilterKeyword.query
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(FilterKeyword.keyword.contains(search))
    
    keywords = query.order_by(FilterKeyword.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    categories = [
        ('PROFANITY', 'Ngôn từ thô tục'),
        ('HARASSMENT', 'Quấy rối, gạ gẫm'),
        ('OFFENSIVE', 'Nội dung xúc phạm'),
        ('SPAM', 'Spam')
    ]
    
    return render_template('keywords.html', 
                         keywords=keywords, 
                         categories=categories,
                         current_category=category,
                         current_search=search)

@app.route('/keywords/add', methods=['GET', 'POST'])
def add_keyword():
    """Thêm từ khóa mới"""
    form = AddKeywordForm()
    
    if form.validate_on_submit():
        # Kiểm tra từ khóa đã tồn tại chưa
        existing = FilterKeyword.query.filter_by(
            keyword=form.keyword.data.lower(),
            category=form.category.data
        ).first()
        
        if existing:
            flash('Từ khóa này đã tồn tại trong danh mục!', 'error')
        else:
            keyword = FilterKeyword(
                keyword=form.keyword.data.lower(),
                category=form.category.data,
                context=form.context.data,
                severity=form.severity.data,
                is_active=form.is_active.data,
                created_by='Admin'
            )
            db.session.add(keyword)
            db.session.commit()
            
            flash('Đã thêm từ khóa thành công!', 'success')
            return redirect(url_for('keywords'))
    
    return render_template('add_keyword.html', form=form)

@app.route('/keywords/edit/<int:keyword_id>', methods=['GET', 'POST'])
def edit_keyword(keyword_id):
    """Chỉnh sửa từ khóa"""
    keyword = FilterKeyword.query.get_or_404(keyword_id)
    form = EditKeywordForm(obj=keyword)
    
    if form.validate_on_submit():
        keyword.keyword = form.keyword.data.lower()
        keyword.category = form.category.data
        keyword.context = form.context.data
        keyword.severity = form.severity.data
        keyword.is_active = form.is_active.data
        
        db.session.commit()
        flash('Đã cập nhật từ khóa thành công!', 'success')
        return redirect(url_for('keywords'))
    
    return render_template('edit_keyword.html', form=form, keyword=keyword)

@app.route('/keywords/delete/<int:keyword_id>', methods=['POST'])
def delete_keyword(keyword_id):
    """Xóa từ khóa"""
    keyword = FilterKeyword.query.get_or_404(keyword_id)
    db.session.delete(keyword)
    db.session.commit()
    
    flash('Đã xóa từ khóa thành công!', 'success')
    return redirect(url_for('keywords'))

@app.route('/keywords/toggle/<int:keyword_id>', methods=['POST'])
def toggle_keyword(keyword_id):
    """Bật/tắt từ khóa"""
    keyword = FilterKeyword.query.get_or_404(keyword_id)
    keyword.is_active = not keyword.is_active
    db.session.commit()
    
    status = 'kích hoạt' if keyword.is_active else 'vô hiệu hóa'
    flash(f'Đã {status} từ khóa thành công!', 'success')
    return redirect(url_for('keywords'))

@app.route('/violations')
def violations():
    """Trang xem lịch sử vi phạm"""
    page = request.args.get('page', 1, type=int)
    violation_type = request.args.get('type', '')
    days = request.args.get('days', 7, type=int)
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = ViolationLog.query.filter(ViolationLog.timestamp >= cutoff_date)
    
    if violation_type:
        query = query.filter_by(violation_type=violation_type)
    
    violations = query.order_by(ViolationLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False)
    
    violation_types = db.session.query(ViolationLog.violation_type).distinct().all()
    violation_types = [vt[0] for vt in violation_types]
    
    return render_template('violations.html',
                         violations=violations,
                         violation_types=violation_types,
                         current_type=violation_type,
                         current_days=days)

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    """Trang cài đặt bot"""
    form = BotSettingsForm()
    
    # Load current settings
    mute_duration = BotSettings.query.filter_by(setting_key='mute_duration').first()
    invite_mute_duration = BotSettings.query.filter_by(setting_key='invite_mute_duration').first()
    ai_moderation = BotSettings.query.filter_by(setting_key='ai_moderation').first()
    
    if request.method == 'GET':
        if mute_duration:
            form.mute_duration.data = mute_duration.setting_value
        else:
            form.mute_duration.data = '10'
            
        if invite_mute_duration:
            form.invite_mute_duration.data = invite_mute_duration.setting_value
        else:
            form.invite_mute_duration.data = '5'
            
        if ai_moderation:
            form.ai_moderation.data = ai_moderation.setting_value == 'true'
        else:
            form.ai_moderation.data = True
    
    if form.validate_on_submit():
        # Update mute duration
        if mute_duration:
            mute_duration.setting_value = form.mute_duration.data
        else:
            mute_duration = BotSettings(
                setting_key='mute_duration',
                setting_value=form.mute_duration.data,
                description='Thời gian mute cho vi phạm thường (phút)'
            )
            db.session.add(mute_duration)
        
        # Update invite mute duration
        if invite_mute_duration:
            invite_mute_duration.setting_value = form.invite_mute_duration.data
        else:
            invite_mute_duration = BotSettings(
                setting_key='invite_mute_duration',
                setting_value=form.invite_mute_duration.data,
                description='Thời gian mute cho link Discord (phút)'
            )
            db.session.add(invite_mute_duration)
        
        # Update AI moderation
        if ai_moderation:
            ai_moderation.setting_value = 'true' if form.ai_moderation.data else 'false'
        else:
            ai_moderation = BotSettings(
                setting_key='ai_moderation',
                setting_value='true' if form.ai_moderation.data else 'false',
                description='Sử dụng AI để kiểm duyệt'
            )
            db.session.add(ai_moderation)
        
        db.session.commit()
        flash('Đã lưu cài đặt thành công!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', form=form)

@app.route('/api/keywords')
def api_keywords():
    """API để bot lấy danh sách từ khóa"""
    keywords = FilterKeyword.query.filter_by(is_active=True).all()
    
    result = {
        'PROFANITY': [],
        'HARASSMENT': [],
        'OFFENSIVE': [],
        'SPAM': []
    }
    
    for keyword in keywords:
        if keyword.category in result:
            result[keyword.category].append({
                'keyword': keyword.keyword,
                'severity': keyword.severity,
                'context': keyword.context
            })
    
    return jsonify(result)

@app.route('/api/settings')
def api_settings():
    """API để bot lấy cài đặt"""
    settings = BotSettings.query.all()
    
    result = {}
    for setting in settings:
        result[setting.setting_key] = setting.setting_value
    
    return jsonify(result)