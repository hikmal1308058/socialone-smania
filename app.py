from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os, uuid
import cloudinary
import cloudinary.uploader
from sqlalchemy import text

app = Flask(__name__, static_folder='static', static_url_path='/static')

DATABASE_URL = (
    os.environ.get('DATABASE_URL') or
    os.environ.get('MYSQL_URL') or
    os.environ.get('MYSQL_PRIVATE_URL')
)

if DATABASE_URL:
    if DATABASE_URL.startswith('mysql://'):
        DATABASE_URL = DATABASE_URL.replace('mysql://', 'mysql+pymysql://', 1)
    elif DATABASE_URL.startswith('mysql+mysqlconnector://'):
        DATABASE_URL = DATABASE_URL.replace('mysql+mysqlconnector://', 'mysql+pymysql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
else:
    DB_USER     = os.environ.get('DB_USER',     'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_HOST     = os.environ.get('DB_HOST',     'localhost')
    DB_PORT     = os.environ.get('DB_PORT',     '3306')
    DB_NAME     = os.environ.get('DB_NAME',     'socialone_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4'
    )

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle':280,'pool_pre_ping':True}
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', ''),
    api_key    = os.environ.get('CLOUDINARY_API_KEY', ''),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', ''),
    secure     = True
)

ALLOWED_IMAGE = {'jpg','jpeg','png','webp','gif'}
ALLOWED_VIDEO = {'mp4','avi','mov','mkv','webm'}
ALLOWED_ALL   = ALLOWED_IMAGE | ALLOWED_VIDEO

db = SQLAlchemy(app)

# ══════════════════════════════════════════════
#  MODELS
# ══════════════════════════════════════════════
class Student(db.Model):
    __tablename__ = 'students'
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100), nullable=False)
    role       = db.Column(db.String(50),  default='Anggota')
    photo      = db.Column(db.String(500), default='')
    hobi       = db.Column(db.String(100), default='—')
    cita       = db.Column(db.String(100), default='—')
    gender     = db.Column(db.String(10),  default='putra')
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    comments   = db.relationship('Comment', backref='student', lazy=True, cascade='all, delete-orphan')
    def to_dict(self):
        return {'id':self.id,'name':self.name,'role':self.role,'photo':self.photo or '','hobi':self.hobi,'cita':self.cita,'gender':self.gender}

class GalleryPhoto(db.Model):
    __tablename__ = 'gallery'
    id         = db.Column(db.Integer, primary_key=True)
    url        = db.Column(db.String(500), nullable=False)
    public_id  = db.Column(db.String(255), default='')
    caption    = db.Column(db.String(255), default='')
    uploader   = db.Column(db.String(100), default='Anonim')
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'url':self.url,'caption':self.caption,'uploader':self.uploader,'created_at':self.created_at.strftime('%d %b %Y')}

class Comment(db.Model):
    __tablename__ = 'comments'
    id         = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    author     = db.Column(db.String(100), nullable=False)
    message    = db.Column(db.Text,        nullable=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'student_id':self.student_id,'author':self.author,'message':self.message,'created_at':self.created_at.strftime('%d %b %Y, %H:%M')}

class Achievement(db.Model):
    __tablename__ = 'achievements'
    id       = db.Column(db.Integer, primary_key=True)
    title    = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), default='Umum')
    year     = db.Column(db.Integer,     default=2023)
    icon     = db.Column(db.String(10),  default='🏆')
    def to_dict(self):
        return {'id':self.id,'title':self.title,'category':self.category,'year':str(self.year),'icon':self.icon}

class AchievementMember(db.Model):
    __tablename__ = 'achievement_members'
    id             = db.Column(db.Integer, primary_key=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False)
    member_name    = db.Column(db.String(100), nullable=False)

class ClassInfo(db.Model):
    __tablename__ = 'class_info'
    id    = db.Column(db.Integer, primary_key=True)
    key   = db.Column(db.String(50),  nullable=False, unique=True)
    value = db.Column(db.String(255), nullable=False)

class Staff(db.Model):
    __tablename__ = 'staff'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), nullable=False)
    role    = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(100), default='')
    type    = db.Column(db.String(20),  default='pejabat')
    def to_dict(self):
        return {'id':self.id,'name':self.name,'role':self.role,'subject':self.subject,'type':self.type}

class Video(db.Model):
    __tablename__ = 'videos'
    id          = db.Column(db.Integer,     primary_key=True)
    title       = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text,        default='')
    video_type  = db.Column(db.String(20),  default='cloudinary')
    url         = db.Column(db.String(500), default='')
    public_id   = db.Column(db.String(255), default='')
    uploader    = db.Column(db.String(100), default='Anonim')
    created_at  = db.Column(db.DateTime,    default=datetime.utcnow)
    def to_dict(self):
        return {'id':self.id,'title':self.title,'description':self.description,'video_type':self.video_type,'url':self.url,'uploader':self.uploader,'created_at':self.created_at.strftime('%d %b %Y')}

# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════
def allowed_file(filename, types=ALLOWED_ALL):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in types

def upload_to_cloudinary(file, folder='socialone', resource_type='image'):
    result = cloudinary.uploader.upload(file, folder=folder, resource_type=resource_type, overwrite=True)
    return result.get('secure_url',''), result.get('public_id','')

# ══════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════
@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/class-info')
def get_class_info():
    rows = ClassInfo.query.all()
    if rows: return jsonify({r.key:r.value for r in rows})
    return jsonify({"name":"XII IPS 1","year":"2020/2023","school":"SMAN 14 PANDEGLANG","motto":"Bersama Meraih Prestasi","members":"33","address":"Jl. Raya Maja Cibiuk Km 7, Pandeglang"})

@app.route('/api/students')
def get_students():
    return jsonify([s.to_dict() for s in Student.query.order_by(Student.id).all()])

@app.route('/api/staff')
def get_staff():
    return jsonify([s.to_dict() for s in Staff.query.order_by(Staff.id).all()])

@app.route('/api/achievements')
def get_achievements():
    items = Achievement.query.order_by(Achievement.id).all()
    return jsonify([a.to_dict() for a in items] if items else [])

@app.route('/api/achievements/<int:aid>/members')
def get_achievement_members(aid):
    rows = db.session.execute(
        text('SELECT member_name FROM achievement_members WHERE achievement_id = :id'),
        {'id': aid}
    ).fetchall()
    return jsonify([r[0] for r in rows])

@app.route('/api/students/<int:sid>/upload-photo', methods=['POST'])
def upload_student_photo(sid):
    s = Student.query.get_or_404(sid)
    if 'photo' not in request.files: return jsonify({'error':'Tidak ada file'}),400
    f = request.files['photo']
    if not f.filename or not allowed_file(f.filename, ALLOWED_IMAGE): return jsonify({'error':'Format tidak valid'}),400
    try:
        url, public_id = upload_to_cloudinary(f, folder='socialone/photos')
        s.photo = url; db.session.commit()
        return jsonify({'success':True,'photo':url})
    except Exception as e:
        return jsonify({'error':f'Upload gagal: {str(e)}'}),500

@app.route('/api/gallery')
def get_gallery():
    return jsonify([p.to_dict() for p in GalleryPhoto.query.order_by(GalleryPhoto.created_at.desc()).all()])

@app.route('/api/gallery/upload', methods=['POST'])
def upload_gallery():
    if 'photo' not in request.files: return jsonify({'error':'Tidak ada file'}),400
    f=request.files['photo']; caption=request.form.get('caption',''); uploader=request.form.get('uploader','Anonim')
    if not f.filename or not allowed_file(f.filename, ALLOWED_IMAGE): return jsonify({'error':'Format tidak valid'}),400
    try:
        url, public_id = upload_to_cloudinary(f, folder='socialone/gallery')
        p=GalleryPhoto(url=url,public_id=public_id,caption=caption,uploader=uploader)
        db.session.add(p); db.session.commit()
        return jsonify({'success':True,'photo':p.to_dict()}),201
    except Exception as e:
        return jsonify({'error':f'Upload gagal: {str(e)}'}),500

@app.route('/api/gallery/<int:pid>', methods=['DELETE'])
def delete_gallery(pid):
    p=GalleryPhoto.query.get_or_404(pid)
    try:
        if p.public_id: cloudinary.uploader.destroy(p.public_id)
    except: pass
    db.session.delete(p); db.session.commit(); return jsonify({'success':True})

@app.route('/api/videos')
def get_videos():
    return jsonify([v.to_dict() for v in Video.query.order_by(Video.created_at.desc()).all()])

@app.route('/api/videos/upload', methods=['POST'])
def upload_video():
    if 'video' not in request.files: return jsonify({'error':'Tidak ada file video'}),400
    f=request.files['video']; title=request.form.get('title','Video Moment')
    desc=request.form.get('description',''); uploader=request.form.get('uploader','Anonim')
    if not f.filename or not allowed_file(f.filename, ALLOWED_VIDEO): return jsonify({'error':'Format tidak valid'}),400
    try:
        url, public_id = upload_to_cloudinary(f, folder='socialone/videos', resource_type='video')
        v=Video(title=title,description=desc,video_type='cloudinary',url=url,public_id=public_id,uploader=uploader)
        db.session.add(v); db.session.commit()
        return jsonify({'success':True,'video':v.to_dict()}),201
    except Exception as e:
        return jsonify({'error':f'Upload gagal: {str(e)}'}),500

@app.route('/api/videos/embed', methods=['POST'])
def embed_video():
    d=request.get_json()
    title=(d.get('title') or 'Video Moment').strip()[:255]
    desc=(d.get('description') or '').strip()
    url=(d.get('url') or '').strip()
    uploader=(d.get('uploader') or 'Anonim').strip()[:100]
    if not url: return jsonify({'error':'URL tidak boleh kosong'}),400
    v=Video(title=title,description=desc,video_type='youtube',url=url,uploader=uploader)
    db.session.add(v); db.session.commit()
    return jsonify({'success':True,'video':v.to_dict()}),201

@app.route('/api/videos/<int:vid>', methods=['DELETE'])
def delete_video(vid):
    v=Video.query.get_or_404(vid)
    try:
        if v.public_id and v.video_type=='cloudinary':
            cloudinary.uploader.destroy(v.public_id,resource_type='video')
    except: pass
    db.session.delete(v); db.session.commit(); return jsonify({'success':True})

@app.route('/api/students/<int:sid>/comments')
def get_comments(sid):
    Student.query.get_or_404(sid)
    return jsonify([c.to_dict() for c in Comment.query.filter_by(student_id=sid).order_by(Comment.created_at.desc()).all()])

@app.route('/api/students/<int:sid>/comments', methods=['POST'])
def post_comment(sid):
    Student.query.get_or_404(sid); d=request.get_json()
    author=(d.get('author') or 'Anonim').strip()[:100]; msg=(d.get('message') or '').strip()
    if not msg: return jsonify({'error':'Pesan kosong'}),400
    c=Comment(student_id=sid,author=author,message=msg); db.session.add(c); db.session.commit()
    return jsonify({'success':True,'comment':c.to_dict()}),201

@app.route('/api/comments/<int:cid>', methods=['DELETE'])
def delete_comment(cid):
    c=Comment.query.get_or_404(cid); db.session.delete(c); db.session.commit(); return jsonify({'success':True})

# ── Admin reset staff ─────────────────────────
@app.route('/admin/reset-staff', methods=['POST'])
def reset_staff():
    data = request.get_json()
    if not data or data.get('secret') != 'reset2024':
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        db.session.execute(text("DELETE FROM staff"))
        db.session.execute(text("""
INSERT INTO staff (name, role, subject, type) VALUES
('Bpk Abdullah Wali','Kepala Sekolah','','pejabat'),
('Ibu Ida Sri Handayani','Wali Kelas','','pejabat'),
('Ibu Sri Yamtini','Wali Kelas','','pejabat'),
('Bpk Ahmad Muhlisin','Guru Mapel','Agama XII','guru'),
('Ibu Neneng','Guru Mapel','Agama X-XI','guru'),
('Ibu Rini Sri Mulyani','Guru Mapel','Ekonomi','guru'),
('Bpk Khojin','Guru Mapel','Sosiologi X','guru'),
('Ibu Putri Ramadyanti','Guru Mapel','Sosiologi XI-XII','guru'),
('Ibu Putri Ramadyanti','Guru Mapel','Bimbingan Konseling X','guru'),
('Ibu Neni Nuraeni','Guru Mapel','Bahasa Indonesia X-XI','guru'),
('Ibu Rahmawati','Guru Mapel','Bahasa Indonesia XII','guru'),
('Bpk Ahmad Fauzi','Guru Mapel','LM Bahasa Arab X-XI','guru'),
('Ibu Ratna Hermawati','Guru Mapel','LM Sejarah','guru'),
('Ibu Neneng','Guru Mapel','Sejarah Wajib XII','guru'),
('Ibu Sri Yamtini','Guru Mapel','Geografi','guru'),
('Bpk Roma Wijaya','Guru Mapel','Penjaskes X-XI','guru'),
('Bpk Darla Effendi','Guru Mapel','Penjaskes XII','guru'),
('Ibu Ida Sri Handayani','Guru Mapel','Bahasa Inggris','guru'),
('Ibu Elis Apriyantini','Guru Mapel','Bahasa Inggris','guru'),
('Bpk Ade Bambang','Guru Mapel','Matematika X-XII','guru'),
('Ibu Wawat Herawati','Guru Mapel','Matematika XI','guru'),
('Ibu Yessi Sofianice','Guru Mapel','Seni Budaya','guru'),
('Bpk Tatang Misbahudin','Guru Mapel','PPKn XII','guru'),
('Ibu Nita Handiani','Guru Mapel','PPKn X-XI','guru'),
('Ibu Eva Khusnul Khatimah','Guru Mapel','PKWU X-XI','guru'),
('Ibu Nita Handiani','Guru Mapel','PKWU XII','guru')
        """))
        db.session.commit()
        return jsonify({'success': True, 'message': '26 staff inserted.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ── Admin seed achievements ────────────────────
@app.route('/admin/seed-achievements', methods=['POST'])
def seed_achievements():
    data = request.get_json()
    if not data or data.get('secret') != 'seed2024':
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        db.session.execute(text("DELETE FROM achievement_members"))
        db.session.execute(text("DELETE FROM achievements"))
        db.session.execute(text("ALTER TABLE achievements AUTO_INCREMENT = 1"))
        db.session.commit()
        achievements_data = [
            ('Monolog','Bulan Bahasa',2021,'🥉'),('Sumpah Pemuda','Bulan Bahasa',2021,'🥉'),('Puisi','Bulan Bahasa',2021,'🏅'),
            ('Debat','Bulan Bahasa',2021,'🥇'),('Duta Bahasa','Bulan Bahasa',2021,'🥈'),('Tari Kreasi','Pentas Seni',2021,'🎭'),
            ('Paduan Suara','Pentas Seni',2021,'🥇'),('Vocal','Pentas Seni',2021,'🎤'),('Modern Dance','Pentas Seni',2021,'💃'),
            ('Dance Challenge','Pentas Seni',2021,'🥇'),('Bazzar','Pentas Seni',2021,'🥇'),('Futsal','Class Meeting',2021,'⚽'),
            ('Voly','Class Meeting',2021,'🏐'),('Tenis Meja','Class Meeting',2021,'🏓'),('Duta Bahasa','Bulan Bahasa',2022,'🥈'),
            ('Debat','Bulan Bahasa',2022,'🥇'),('Monolog','Bulan Bahasa',2022,'🥉'),('Puisi','Bulan Bahasa',2022,'🏅'),
            ('Stand Up Comedy','Bulan Bahasa',2022,'🥇'),('Tari Kreasi','Pentas Seni',2022,'🎭'),('Dance Modern','Pentas Seni',2022,'💃'),
            ('Dance Challenge','Pentas Seni',2022,'🥇'),('Vocal Putra','Pentas Seni',2022,'🎤'),('Vocal Putri','Pentas Seni',2022,'🎤'),
            ('Music Kreasi','Pentas Seni',2022,'🎵'),('Bazzar','Pentas Seni',2022,'🥇'),('Teacher Cover','Hari Guru',2022,'🏅'),
            ('Futsal Cup Smania','Futsal Cup',2023,'🎖️'),
        ]
        for title, category, year, icon in achievements_data:
            a = Achievement(title=title, category=category, year=year, icon=icon)
            db.session.add(a)
        db.session.commit()
        members_data = {
            1:['Rahayu Abadiah'],2:['Sumitra'],3:['Imas Masruroh'],4:['Erlangga','Rianti','Hidayati'],5:['Sumitra'],
            6:['Erlangga','Mitra','Rianti','Hildayanti'],7:['Seluruh Anggota Kelas'],8:['Sumitra','Dewi Kusumawati'],
            9:['Mila Anggelina','Rahayu Abadiah'],10:['Gilang','Fahrurozi','Dimas','Irfan','Arya','Danu','Erlangga','Rizki','Virdiansyah','Sumitra','Bima','Waseh'],
            11:['Naftalia','Imas','Rendi','Ridwan'],12:['Ridwan','Irfan','Gilang','Waseh','Bima','Fahru','Dimas','Arya','Amin'],
            13:['Anisa','Erusmiati','Hildayanti','Dini','Mila','Rahayu','Sindi'],14:['Dewi Kusumawati','Aminuddin'],15:['Sumitra'],
            16:['Erlangga','Dewi Kusumawati','Arya Pratama'],17:['Rahayu Abadiah'],18:['Imas Masruroh'],19:['Aminuddin'],
            20:['Anisa','Erusmiati','Mila','Rahayu','Sindi','Imas'],21:['Mila Anggelina','Rahayu Abadiah'],
            22:['Erlangga','Arya','Hikmal','Danu','Waseh','Haikal','Sumitra'],23:['Sumitra'],24:['Dewi Kusumawati'],
            25:['Aminuddin','Fahrurozi','Dimas','Gilang','Arya','Irfan'],26:['Naftalia','Solehah','Dini','Rendi','Febriansyah'],
            27:['Erlangga','Dewi Kusumawati'],28:['Arya','Aminuddin','Waseh','Irfan','Fahrurozi','Dimas','Gilang','Febriansyah'],
        }
        for aid, members in members_data.items():
            for member in members:
                am = AchievementMember(achievement_id=aid, member_name=member)
                db.session.add(am)
        db.session.commit()
        return jsonify({'success': True, 'message': f'{len(achievements_data)} prestasi & {sum(len(m) for m in members_data.values())} anggota ditambahkan.'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ══════════════════════════════════════════════
#  JALANKAN
# ══════════════════════════════════════════════
if __name__ == '__main__':
    with app.app_context():
        try:
            db.engine.connect()
            print("✅ Berhasil terhubung ke database")
        except Exception as e:
            print(f"❌ Gagal koneksi: {e}")
    app.run(debug=True, port=5000)