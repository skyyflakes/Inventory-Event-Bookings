from flask import Flask, render_template, jsonify, request, redirect, url_for, session, flash
from models import db, User, Category, Inventory, Event, Report
from config import Config
from datetime import datetime
import random
import string
import uuid

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)


# --- UTILITY: Captcha Generator ---
def generate_captcha():
    """Gumagawa ng 5 random characters para sa captcha."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))


# --- MIDDLEWARE: Security Check ---
@app.before_request
def check_login():
    allowed_routes = ['login', 'static']
    if 'user_id' not in session and request.endpoint not in allowed_routes:
        if request.endpoint and 'static' not in request.endpoint:
            return redirect(url_for('login'))


# --- DASHBOARD ---
@app.route('/')
def dashboard():
    low_stock_count = Inventory.query.filter(Inventory.ending_qty <= 10).count()
    total_varieties = Inventory.query.count()
    total_events = Event.query.count()
    pending_events = Event.query.filter_by(status='Pending').count()
    confirmed_events = Event.query.filter_by(status='Confirmed').count()
    total_reports = Report.query.count()

    # FIX: Ipinapasa ang role at username sa template para sa sidebar role display
    return render_template('dashboard.html',
                           low_stock=low_stock_count,
                           total_varieties=total_varieties,
                           total_events=total_events,
                           pending_events=pending_events,
                           confirmed_events=confirmed_events,
                           total_reports=total_reports,
                           role=session.get('role', 'ADMIN'),
                           username=session.get('username', 'User'))


# --- EVENT LIST ---
@app.route('/events')
def event_list():
    events = Event.query.order_by(Event.event_date.desc()).all()
    # FIX: Ipinapasa ang role at username sa template
    return render_template('events.html', events=events,
                           role=session.get('role', 'ADMIN'),
                           username=session.get('username', 'User'))


# --- EVENT BOOKING (GET = form, POST = save) ---
@app.route('/events/booking', methods=['GET', 'POST'])
def event_booking():
    if request.method == 'POST':
        # FIX: Kinukuha lahat ng fields mula sa eventform.html form names
        new_event = Event(
            id=str(uuid.uuid4()),
            fullname=request.form.get('fullname'),
            email=request.form.get('email'),
            contact=request.form.get('contact'),
            customer_address=request.form.get('customer_address'),
            event_name=request.form.get('event_type'),
            event_date=datetime.strptime(request.form.get('event_date'), '%Y-%m-%d'),
            pax=int(request.form.get('pax', 50)),
            province=request.form.get('province'),
            city=request.form.get('city'),
            barangay=request.form.get('barangay'),
            venue_address=request.form.get('venue_address'),
            status='Pending',
            backdrop=request.form.get('backdrop_name', session.get('selected_backdrop', 'None'))
        )
        db.session.add(new_event)
        db.session.commit()

        session.pop('selected_backdrop', None)
        flash('Event booked successfully!', 'success')
        return redirect(url_for('event_list'))

    selected = session.get('selected_backdrop')
    # FIX: Tama na ang render sa eventform.html (hindi event.html)
    return render_template('eventform.html', selected_backdrop=selected)


# --- EVENT STATUS UPDATE ---
@app.route('/events/update_status/<event_id>', methods=['POST'])
def update_event_status(event_id):
    event = Event.query.get_or_404(event_id)
    new_status = request.form.get('status')
    if new_status in ['Pending', 'Confirmed', 'Cancelled', 'Completed']:
        event.status = new_status
        db.session.commit()
        flash(f'Event status updated to {new_status}!', 'success')
    else:
        flash('Invalid status!', 'danger')
    return redirect(url_for('event_list'))


# --- EVENT DELETE ---
@app.route('/events/delete/<event_id>', methods=['POST'])
def delete_event(event_id):
    if session.get('role') != 'OWNER':
        flash('Unauthorized! Only OWNER can delete events.', 'danger')
        return redirect(url_for('event_list'))
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully!', 'success')
    return redirect(url_for('event_list'))


# --- BACKDROPS ---
@app.route('/backdrops')
def backdrops_page():
    photos = [f"photo{i}.jpg" for i in range(1, 71)]
    return render_template('backdrops.html', photos=photos)


@app.route('/select_backdrop', methods=['POST'])
def select_backdrop():
    photo_name = request.form.get('photo_name')
    session['selected_backdrop'] = photo_name
    flash(f'Backdrop {photo_name} selected! Proceed to booking.', 'success')
    return redirect(url_for('event_booking'))


# --- INVENTORY ---
@app.route('/inventory')
def inventory_page():
    categories = Category.query.all()
    inventory_data = {}

    for cat in categories:
        items = Inventory.query.filter_by(category_id=cat.category_id, is_active=True).all()
        inventory_data[cat.category_name] = items

    return render_template('inventory.html', inventory_data=inventory_data,
                           role=session.get('role', 'ADMIN'),
                           username=session.get('username', 'User'))


# --- INVENTORY ADD ITEM ---
@app.route('/inventory/add', methods=['POST'])
def add_inventory_item():
    if session.get('role') != 'OWNER':
        flash('Unauthorized! Only OWNER can add items.', 'danger')
        return redirect(url_for('inventory_page'))

    new_item = Inventory(
        item_id=str(uuid.uuid4()),
        category_id=int(request.form.get('category_id')),
        item_name=request.form.get('item_name'),
        beginning_qty=int(request.form.get('beginning_qty', 0)),
        previous_qty=int(request.form.get('previous_qty', 0)),
        extra_qty=int(request.form.get('extra_qty', 0)),
        ending_qty=int(request.form.get('ending_qty', 0)),
        is_active=True
    )
    db.session.add(new_item)
    db.session.commit()
    flash('Item added successfully!', 'success')
    return redirect(url_for('inventory_page'))


# --- INVENTORY EDIT ITEM ---
@app.route('/inventory/edit/<item_id>', methods=['POST'])
def edit_inventory_item(item_id):
    if session.get('role') != 'OWNER':
        flash('Unauthorized! Only OWNER can edit items.', 'danger')
        return redirect(url_for('inventory_page'))

    item = Inventory.query.get_or_404(item_id)
    item.item_name = request.form.get('item_name', item.item_name)
    item.beginning_qty = int(request.form.get('beginning_qty', item.beginning_qty))
    item.previous_qty = int(request.form.get('previous_qty', item.previous_qty))
    item.extra_qty = int(request.form.get('extra_qty', item.extra_qty))
    item.ending_qty = int(request.form.get('ending_qty', item.ending_qty))
    db.session.commit()
    flash('Item updated successfully!', 'success')
    return redirect(url_for('inventory_page'))


# --- INVENTORY DELETE ITEM ---
@app.route('/inventory/delete/<item_id>', methods=['POST'])
def delete_inventory_item(item_id):
    if session.get('role') != 'OWNER':
        flash('Unauthorized! Only OWNER can delete items.', 'danger')
        return redirect(url_for('inventory_page'))

    item = Inventory.query.get_or_404(item_id)
    item.is_active = False  # Soft delete para di mawala sa records
    db.session.commit()
    flash('Item removed from inventory!', 'success')
    return redirect(url_for('inventory_page'))


# --- REPORTS ---
@app.route('/reports')
def reports_page():
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('reports.html', reports=reports,
                           role=session.get('role', 'ADMIN'),
                           username=session.get('username', 'User'))


# --- REPORT CREATE ---
@app.route('/reports/create', methods=['POST'])
def create_report():
    if session.get('role') != 'OWNER':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('reports_page'))

    new_rep = Report(
        id=str(uuid.uuid4()),
        title=request.form.get('title'),
        content=request.form.get('content'),
        # FIX: Ginagamit ang created_at (hindi date_created) na tugma sa model
        created_at=datetime.now(),
        created_by=session.get('username'),
        status='Generated'
    )
    db.session.add(new_rep)
    db.session.commit()
    flash('Report created successfully!', 'success')
    return redirect(url_for('reports_page'))


# --- REPORT EDIT ---
@app.route('/reports/edit/<report_id>', methods=['POST'])
def edit_report(report_id):
    if session.get('role') != 'OWNER':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('reports_page'))

    report = Report.query.get_or_404(report_id)
    report.title = request.form.get('title', report.title)
    report.content = request.form.get('content', report.content)
    db.session.commit()
    flash('Report updated successfully!', 'success')
    return redirect(url_for('reports_page'))


# --- REPORT DELETE ---
@app.route('/reports/delete/<report_id>', methods=['POST'])
def delete_report(report_id):
    if session.get('role') != 'OWNER':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('reports_page'))

    report = Report.query.get_or_404(report_id)
    db.session.delete(report)
    db.session.commit()
    flash('Report deleted successfully!', 'success')
    return redirect(url_for('reports_page'))


# --- AUTH ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_captcha = request.form.get('captcha_input')
        terms_accepted = request.form.get('terms')

        if not terms_accepted:
            flash('You must agree to terms.', 'warning')
            return render_template('login.html', captcha=session.get('captcha_text'))

        if user_captcha != session.get('captcha_text'):
            flash('Invalid Captcha!', 'danger')
            session['captcha_text'] = generate_captcha()
            return render_template('login.html', captcha=session.get('captcha_text'))

        # DB User Login Logic
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session.update({'user_id': user.id, 'role': user.role, 'username': user.username})
            return redirect(url_for('dashboard'))

        # Hardcoded Fallback para sa initial setup
        if username == 'admin' and password == 'admin123':
            session.update({'user_id': 'admin-id', 'role': 'ADMIN', 'username': 'admin'})
            return redirect(url_for('dashboard'))

        flash('Invalid credentials!', 'danger')
        session['captcha_text'] = generate_captcha()
        return render_template('login.html', captcha=session.get('captcha_text'))

    session['captcha_text'] = generate_captcha()
    return render_template('login.html', captcha=session['captcha_text'])


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


# --- API ENDPOINTS PARA SA DASHBOARD STATS (AJAX) ---
@app.route('/api/dashboard-stats')
def dashboard_stats():
    """Returns JSON data para sa dashboard charts at stats"""
    low_stock = Inventory.query.filter(Inventory.ending_qty <= 10).count()
    total_varieties = Inventory.query.count()
    total_events = Event.query.count()
    pending = Event.query.filter_by(status='Pending').count()
    confirmed = Event.query.filter_by(status='Confirmed').count()
    total_reports = Report.query.count()

    return jsonify({
        'low_stock': low_stock,
        'total_varieties': total_varieties,
        'total_events': total_events,
        'pending_events': pending,
        'confirmed_events': confirmed,
        'total_reports': total_reports
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
