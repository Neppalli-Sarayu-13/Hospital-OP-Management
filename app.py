from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

# Temporary storage
users = []
visits = []

# ===== HOME =====
@app.route('/')
def home():
    return render_template('home.html')


# ===== REGISTER =====
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            error = "Passwords do not match"
        elif any(user['email'] == email for user in users):
            error = "Email already registered"
        else:
            users.append({'username': username, 'email': email, 'password': password})
            return redirect(url_for('login'))

    return render_template('register.html', error=error)


# ===== LOGIN =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        for user in users:
            if user['email'] == email and user['password'] == password:
                session['user'] = email
                return redirect(url_for('dashboard'))
        error = "Invalid email or password"
    return render_template('login.html', error=error)


# ===== DASHBOARD =====
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', user=session['user'])


# ===== LOGOUT =====
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))



# ===== ADD VISIT =====
@app.route('/add_visit', methods=['GET', 'POST'])
def add_visit():
    if 'user' not in session:
        return redirect(url_for('login'))

    error = None
    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        visit_date = request.form.get('visit_date')
        purpose = request.form.get('purpose')
        notes = request.form.get('notes')

        if not customer_name or not visit_date or not purpose:
            error = "Please fill in all required fields"
        else:
            visits.append({
                'user': session['user'],
                'customer_name': customer_name,
                'visit_date': visit_date,
                'purpose': purpose,
                'notes': notes
            })
            return redirect(url_for('view_visits'))

    return render_template('add_visit.html', error=error)


# ===== VIEW VISITS =====
@app.route('/view_visits')
def view_visits():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_visits = [v for v in visits if v['user'] == session['user']]
    return render_template('view_visits.html', visits=user_visits)


# ===== UPDATE VISIT =====
@app.route('/update_visit')
def update_visit_list():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_visits = [v for v in visits if v['user'] == session['user']]
    return render_template('update_visit_list.html', visits=user_visits)


@app.route('/edit_visit/<int:index>', methods=['GET', 'POST'])
def edit_visit(index):
    if 'user' not in session:
        return redirect(url_for('login'))  # Ensure user is logged in

    # Check if index is valid and belongs to current user
    if index < 0 or index >= len(visits) or visits[index]['user'] != session['user']:
        return "Invalid visit", 404

    visit = visits[index]
    error = None

    if request.method == 'POST':
        customer_name = request.form.get('customer_name')
        visit_date = request.form.get('visit_date')
        purpose = request.form.get('purpose')
        notes = request.form.get('notes')

        # Validate required fields
        if not customer_name or not visit_date or not purpose:
            error = "Please fill in all required fields"
        else:
            # Update visit info
            visit['customer_name'] = customer_name
            visit['visit_date'] = visit_date
            visit['purpose'] = purpose
            visit['notes'] = notes

            return redirect(url_for('update_visit_list'))  # Redirect after update

    return render_template('edit_visit.html', visit=visit, error=error, index=index)


# ===== DELETE VISIT =====
@app.route('/delete_visit')
def delete_visit_list():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_visits = [v for v in visits if v['user'] == session['user']]
    return render_template('delete_visit.html', visits=user_visits)


@app.route('/delete_visit/<int:index>')
def delete_visit(index):
    if 'user' not in session:
        return redirect(url_for('login'))
    if index < 0 or index >= len(visits) or visits[index]['user'] != session['user']:
        return "Invalid visit", 404
    visits.pop(index)
    return redirect(url_for('delete_visit_list'))



# ===== RUN APP =====
if __name__ == '__main__':
    app.run(debug=True)
