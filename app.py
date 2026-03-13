import streamlit as st
from data_manager import init_db, load_full_db
from stages_1_2 import render_stage1, render_stage2
from stage_3 import render_stage3
from stage_4 import render_stage4
from stage_5 import render_stage5
from stage_6 import render_stage6
from stage_7 import render_stage7

# إعدادات الصفحة و الـ CSS
st.set_page_config(page_title="نظام الجداول", layout="wide")

st.markdown("""
<style>
/* 🌟 استدعاء الخط العربي Tajawal من جوجل 🌟 */
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;900&display=swap');

/* 🌟 تطبيق الخط على التطبيق بالكامل 🌟 */
html, body, [class*="css"] {
    font-family: 'Tajawal', sans-serif !important;
}

/* توجيه النصوص والواجهة لليمين */
h1, h2, h3, h4, h5, h6, p, .stMarkdown, .stText { 
    direction: rtl !important; 
    text-align: right !important; 
    font-family: 'Tajawal', sans-serif !important; 
}
.stApp { direction: rtl !important; }
input, textarea, select, .stSelectbox { 
    direction: rtl !important; 
    text-align: right !important; 
    font-family: 'Tajawal', sans-serif !important; 
}

/* 🌟 السماح للتبويبات بالنزول لسطر جديد عند امتلاء الشاشة 🌟 */
div[data-baseweb="tab-list"] { 
    display: flex; 
    flex-direction: row; 
    flex-wrap: wrap; /* السطر المسؤول عن كسر السطر */
    justify-content: flex-start; 
    gap: 10px; 
}

/* تصميم إطار التبويب (الصندوق غير النشط) */
.stTabs [data-baseweb="tab-list"] button {
    background-color: #ffffff !important; 
    border: 2px solid #1c83e1 !important;
    border-radius: 10px !important;
    padding: 12px 20px !important;
    font-size: 18px !important;
    font-weight: 900 !important;
    color: #1c83e1 !important;
    transition: all 0.3s ease-in-out !important;
    box-shadow: 2px 2px 5px rgba(0,0,0,0.05) !important;
    font-family: 'Tajawal', sans-serif !important;
}

.stTabs [data-baseweb="tab-list"] button span,
.stTabs [data-baseweb="tab-list"] button p {
    font-weight: 900 !important;
    font-size: 18px !important;
    font-family: 'Tajawal', sans-serif !important;
}

.stTabs [data-baseweb="tab-list"] button:hover {
    background-color: #e6f2ff !important;
    transform: translateY(-2px) !important;
}

/* تصميم التبويب النشط (المفتوح حالياً) */
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: #1c83e1 !important;
    border-bottom-color: #1c83e1 !important;
    color: #ffffff !important;
    box-shadow: 0px 4px 10px rgba(28,131,225,0.4) !important;
}

.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] span,
.stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {
    color: #ffffff !important;
}

/* إخفاء شريط السحب الجانبي (Resizer) لمنع ظهور الخط العمودي */
[data-testid="stSidebarResizer"] {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)

# تهيئة وإدارة قاعدة البيانات
init_db()
st.session_state.db = load_full_db()

# =========================================
# العنوان الرئيسي
# =========================================
st.markdown("""
<div style="background-color: #dceaf6; border: 3px solid #0b5394; border-radius: 15px; padding: 25px; margin-top: 10px; margin-bottom: 35px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); display: flex; justify-content: center; align-items: center;">
    <h1 style="color: #0b5394; margin: 0; font-size: 38px; font-weight: bold; text-align: center !important; text-shadow: 1px 1px 2px rgba(0,0,0,0.1); font-family: 'Tajawal', sans-serif !important;">
        نظام الجداول وتوزيع المواد للامتحانات الاستدراكية
    </h1>
</div>
""", unsafe_allow_html=True)

# التبويبات والمراحل
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "1. إدخال البيانات", "2. التعديل", "3. إسناد المواد", 
    "4. تخصيص القاعات", "5. الأيام والأوقات", "6. القيود", "7. التوزيع"
])

with tab1: render_stage1()
with tab2: render_stage2()
with tab3: render_stage3()
with tab4: render_stage4()
with tab5: render_stage5()
with tab6: render_stage6()
with tab7: render_stage7()