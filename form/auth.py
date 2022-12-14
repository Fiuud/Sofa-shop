from flask import render_template, request, session, redirect, flash
from database.extension import execute_read_query, execute_query
from passlib.hash import sha256_crypt


# REGISTRATION
def reg():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email_reg']
        password = sha256_crypt.encrypt(request.form['password_reg'])
        check_sql = f'''select * from `user` where email = '{email}' '''
        account = execute_read_query(check_sql)
        status = True
        if account:
            status = False
            flash('Этот email уже занят.', category='warning')
        if first_name[0].islower() or last_name[0].islower():
            status = False
            flash('Имя и фамилия должны начинаться с заглавных букв.', category='warning')
        if len(request.form['password_reg']) < 8:
            status = False
            flash('Пароль должен содержать не менее 8 символов.', category='warning')
        if status:
            write_sql = f'''INSERT INTO `user` (`email`, `password`, `first_name`, `last_name`, `address`,`admin`) 
            VALUES ('{email}', '{password}', '{first_name}', '{last_name}', '', 0)'''
            execute_query(write_sql)
            flash('Аккаунт создан.', category='success')
            return redirect('/login')
    return redirect('/login')


# LOGIN
def login():
    if (request.referrer != request.url_root + 'login') and (request.referrer != request.url_root + 'reg'):
        session['request'] = request.referrer
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        check_sql = f'''select * from user where email = '{email}' '''
        login_user = execute_read_query(check_sql)
        print(password)
        if login_user == tuple():
            flash('Неверный никнейм или пароль.', category='danger')
            return redirect('/login')
        else:
            login_user = login_user[0]
            print(login_user['password'])
            if sha256_crypt.verify(password, login_user['password']):

                session['logged_in'] = True
                session['first_name'] = login_user['first_name']
                session['last_name'] = login_user['last_name']
                session['email'] = login_user['email']
                session['user_id'] = login_user['id']
                session['admin'] = login_user['admin']
                session['address'] = login_user['address']

                check_actual_order = f'''SELECT id FROM orders
                                                    where idUser = {session.get('user_id')} and actual = 1'''
                actual_order = execute_read_query(check_actual_order)
                if actual_order != tuple():
                    check_total_count = f'''SELECT sum(order_product.count) as total_count FROM order_product 
                                                            where idOrder='{actual_order[0]['id']}' '''
                    total_count = execute_read_query(check_total_count)[0]['total_count']
                    session['count_product_cart'] = total_count
                if session.get('request'):
                    return redirect(session.get('request'))
                return redirect('/')
            else:
                flash('Неверный никнейм или пароль.', category='danger')
                return redirect('/login')

    return render_template('auth.html')


# ACCOUNT LOGOUT
def exit_account():
    session.clear()
    session['request'] = request.referrer
    return redirect(session.get('request'))
