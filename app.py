from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import qrcode
import io
import base64

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
db = SQLAlchemy(app)

class Box(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contents = db.Column(db.Text, nullable=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    boxes = Box.query.all()
    return render_template('index.html', boxes=boxes)

@app.route('/add_box', methods=['POST'])
def add_box():
    name = request.form['name']
    contents = request.form['contents']
    new_box = Box(name=name, contents=contents)
    db.session.add(new_box)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/view_box/<int:id>')
def view_box(id):
    box = Box.query.get_or_404(id)
    return render_template('view_box.html', box=box)

@app.route('/edit_box/<int:id>', methods=['GET', 'POST'])
def edit_box(id):
    box = Box.query.get_or_404(id)
    if request.method == 'POST':
        box.name = request.form['name']
        box.contents = request.form['contents']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_box.html', box=box)

@app.route('/delete_box/<int:id>')
def delete_box(id):
    box = Box.query.get_or_404(id)
    db.session.delete(box)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/qr_code/<int:id>')
def qr_code(id):
    box_url = url_for('view_box', id=id, _external=True)
    img = qrcode.make(box_url)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_data = base64.b64encode(img_io.getvalue()).decode()
    return render_template('qr_code.html', img_data=img_data)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5003)