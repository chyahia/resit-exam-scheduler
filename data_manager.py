import sqlite3
import json
import os

DB_PATH = "schedule_database.db"

def get_connection():
    """إنشاء اتصال بقاعدة البيانات"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # للحصول على النتائج كقواميس
    return conn

def init_db():
    """إنشاء الجداول إذا لم تكن موجودة"""
    conn = get_connection()
    c = conn.cursor()
    
    # جداول الكيانات الأساسية (علائقية)
    c.execute('''CREATE TABLE IF NOT EXISTS teachers (name TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS rooms (name TEXT PRIMARY KEY, type TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS levels (name TEXT PRIMARY KEY)''')
    c.execute('''CREATE TABLE IF NOT EXISTS subjects (name TEXT, level TEXT, PRIMARY KEY(name, level))''')
    
    # جدول لتخزين البيانات المعقدة (JSON Blobs)
    c.execute('''CREATE TABLE IF NOT EXISTS complex_state (key TEXT PRIMARY KEY, data_json TEXT)''')
    
    conn.commit()
    conn.close()
    
    # تهيئة البيانات المعقدة الافتراضية إذا كانت قاعدة البيانات جديدة
    _init_default_complex_state()

def _init_default_complex_state():
    """تهيئة القواميس الافتراضية في قاعدة البيانات"""
    conn = get_connection()
    c = conn.cursor()
    defaults = {
        "teacher_subjects": {},
        "level_rooms": {},
        "schedule": {},
        "constraints": {
            "invigilators_per_room": {"قاعة كبيرة": 3, "قاعة متوسطة": 2, "قاعة صغيرة": 1},
            "max_shifts_per_day": 0,
            "max_large_hall_shifts": 0,
            "teacher_patterns": {},
            "incompatible_levels": [],
            "prioritized_teachers": [],
            "carpool_pairs": [],
            "conflict_pairs": [],
            "no_first_slot_teachers": []
        }
    }
    for key, val in defaults.items():
        c.execute("INSERT OR IGNORE INTO complex_state (key, data_json) VALUES (?, ?)", (key, json.dumps(val, ensure_ascii=False)))
    conn.commit()
    conn.close()

# ==========================================
# دوال التجميع (لجلب البيانات كقاموس واحد متكامل للواجهة والمحرك)
# ==========================================
def load_full_db():
    """تجلب جميع البيانات من SQLite وتعيدها على شكل قاموس (نفس الهيكل القديم)"""
    conn = get_connection()
    c = conn.cursor()
    
    db_dict = {}
    
    # جلب القوائم الأساسية
    db_dict['teachers'] = [row['name'] for row in c.execute("SELECT name FROM teachers")]
    db_dict['rooms'] = {row['name']: row['type'] for row in c.execute("SELECT name, type FROM rooms")}
    db_dict['levels'] = [row['name'] for row in c.execute("SELECT name FROM levels")]
    db_dict['subjects'] = [{"name": row['name'], "level": row['level']} for row in c.execute("SELECT name, level FROM subjects")]
    
    # جلب البيانات المعقدة
    c.execute("SELECT key, data_json FROM complex_state")
    for row in c.fetchall():
        db_dict[row['key']] = json.loads(row['data_json'])
        
    conn.close()
    return db_dict

# ==========================================
# دوال التعديل المباشر (تستخدمها الواجهات)
# ==========================================
def execute_query(query, params=()):
    """دالة مساعدة لتنفيذ الاستعلامات وحفظها"""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(query, params)
        conn.commit()
    except sqlite3.IntegrityError:
        pass # تجاهل الإدخالات المكررة
    finally:
        conn.close()

# --- إدارة الأساتذة ---
def add_teacher(name): execute_query("INSERT INTO teachers (name) VALUES (?)", (name,))
def remove_teacher(name): execute_query("DELETE FROM teachers WHERE name = ?", (name,))

# --- إدارة القاعات ---
def add_room(name, r_type): execute_query("INSERT INTO rooms (name, type) VALUES (?, ?)", (name, r_type))
def remove_room(name): execute_query("DELETE FROM rooms WHERE name = ?", (name,))

# --- إدارة المستويات ---
def add_level(name): execute_query("INSERT INTO levels (name) VALUES (?)", (name,))
def remove_level(name): execute_query("DELETE FROM levels WHERE name = ?", (name,))

# --- إدارة المواد ---
def add_subject(name, level): execute_query("INSERT INTO subjects (name, level) VALUES (?, ?)", (name, level))
def remove_subject(name, level): execute_query("DELETE FROM subjects WHERE name = ? AND level = ?", (name, level))

# --- إدارة البيانات المعقدة ---
def update_complex_state(key, data_dict):
    """تحديث الجداول الزمنية، القيود، وإسناد المواد"""
    execute_query("UPDATE complex_state SET data_json = ? WHERE key = ?", (json.dumps(data_dict, ensure_ascii=False), key))

# ==========================================
# دالة استيراد البيانات من ملف JSON
# ==========================================
def import_from_json(json_string):
    """تستقبل محتوى ملف JSON وتقوم بتفريغه في جداول SQLite"""
    try:
        data = json.loads(json_string)
        conn = get_connection()
        c = conn.cursor()
        
        # مسح البيانات القديمة لضمان استيراد نظيف
        c.execute("DELETE FROM teachers")
        c.execute("DELETE FROM rooms")
        c.execute("DELETE FROM levels")
        c.execute("DELETE FROM subjects")
        
        # إدراج الأساتذة
        for t in data.get("teachers", []):
            c.execute("INSERT OR IGNORE INTO teachers (name) VALUES (?)", (t,))
            
        # إدراج القاعات
        for r_name, r_type in data.get("rooms", {}).items():
            c.execute("INSERT OR IGNORE INTO rooms (name, type) VALUES (?, ?)", (r_name, r_type))
            
        # إدراج المستويات
        for lvl in data.get("levels", []):
            c.execute("INSERT OR IGNORE INTO levels (name) VALUES (?)", (lvl,))
            
        # إدراج المواد
        for sub in data.get("subjects", []):
            c.execute("INSERT OR IGNORE INTO subjects (name, level) VALUES (?, ?)", (sub.get("name"), sub.get("level")))
            
        # إدراج الحالات المعقدة
        complex_keys = ["teacher_subjects", "level_rooms", "schedule", "constraints"]
        for key in complex_keys:
            if key in data:
                c.execute("UPDATE complex_state SET data_json = ? WHERE key = ?", (json.dumps(data[key], ensure_ascii=False), key))
                
        conn.commit()
        conn.close()
        return True, "تم استيراد البيانات وتحديث قاعدة البيانات بنجاح."
    except Exception as e:
        return False, f"حدث خطأ أثناء الاستيراد: {str(e)}"