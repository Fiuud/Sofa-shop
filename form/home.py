from flask import render_template
from database.extension import execute_read_query


# HOME
def home():
    check_products = '''SELECT product.id, color_id, picture, product.title, product.price, color_id
                FROM product, product_has_color where count>0 
                and product_has_color.product_id = product.id group by product.title'''
    products = execute_read_query(check_products)
    return render_template('home.html', products=products)


# ABOUT
def about():
    return render_template('about.html')
