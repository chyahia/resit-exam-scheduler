import streamlit as st
from data_manager import update_complex_state

def render_stage6():
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 20px; padding: 15px; border: 2px solid #1c83e1; border-radius: 10px; background-color: rgba(28,131,225,0.1); font-weight: bold;'>
        6. القيود والشروط (الاستدراكية)
    </h2>
    """, unsafe_allow_html=True)
    
    st.info("💡 **تنبيه:** الخوارزمية تعطي الأولوية المطلقة لعدم تعارض المستويات (قيد صارم)، ثم لتجميع مواد الأساتذة ذوي الأولوية في أقل عدد من الأيام (أقوى قيد مرن).")

    if not st.session_state.db['levels']:
        st.warning("⚠️ يرجى إدخال المستويات في المرحلة الأولى أولاً.")
        return

    # تهيئة ذواكر القيود الجديدة
    if 'constraints' not in st.session_state.db:
        st.session_state.db['constraints'] = {}
    
    c_db = st.session_state.db['constraints']
    if 'incompatible_levels' not in c_db: c_db['incompatible_levels'] = []
    if 'prioritized_teachers' not in c_db: c_db['prioritized_teachers'] = []
    if 'carpool_pairs' not in c_db: c_db['carpool_pairs'] = []
    if 'conflict_pairs' not in c_db: c_db['conflict_pairs'] = []
    if 'no_first_slot_teachers' not in c_db: c_db['no_first_slot_teachers'] = []

    st.markdown("---")
    
    # استخدام التبويبات لتنظيم الشاشة
    tab1, tab2, tab3 = st.tabs(["🚫 قيود المستويات (صارمة)", "⭐ أولويات الأساتذة (مرنة)", "🤝 علاقات الأساتذة (مرنة)"])
    
    # =======================================
    # التبويب 1: القيود الصارمة (التعارض)
    # =======================================
    with tab1:
        st.subheader("منع التعارض بين المستويات")
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                level_a = st.selectbox("المستوى الأول:", st.session_state.db['levels'], key="lvl_a")
                level_b = st.selectbox("المستوى الثاني:", st.session_state.db['levels'], key="lvl_b")
                if st.button("➕ إضافة قيد المنع", use_container_width=True):
                    if level_a != level_b:
                        new_rule = sorted([level_a, level_b])
                        if new_rule not in c_db['incompatible_levels']:
                            c_db['incompatible_levels'].append(new_rule)
                            update_complex_state('constraints', c_db)
                            st.success("تمت الإضافة!")
                            st.rerun()

        with col2:
            with st.container(border=True, height=220):
                for idx, rule in enumerate(c_db['incompatible_levels']):
                    r_c1, r_c2 = st.columns([4, 1])
                    r_c1.markdown(f"❌ `{rule[0]}` مع `{rule[1]}`")
                    if r_c2.button("حذف", key=f"del_rule_{idx}"):
                        c_db['incompatible_levels'].pop(idx)
                        update_complex_state('constraints', c_db)
                        st.rerun()

    # =======================================
    # التبويب 2: أولويات الأساتذة (المرنة الأساسية)
    # =======================================
    with tab2:
        st.subheader("تجميع الأيام وتأخير الحصة الأولى")
        col3, col4 = st.columns(2)
        with col3:
            with st.container(border=True):
                st.write("**الأساتذة ذوو الأولوية (تجميع الأيام):**")
                prioritized = st.multiselect(
                    "اختر الأساتذة:", 
                    st.session_state.db['teachers'],
                    default=c_db['prioritized_teachers']
                )
        with col4:
            with st.container(border=True):
                st.write("**الإعفاء من الحصة الأولى في أول يوم:**")
                no_first_slot = st.multiselect(
                    "اختر الأساتذة:", 
                    st.session_state.db['teachers'],
                    default=c_db['no_first_slot_teachers'],
                    help="هؤلاء الأساتذة لن تبدأ امتحاناتهم في أول فترة زمنية من أول يوم عمل لهم."
                )
        
        if st.button("💾 حفظ أولويات الأساتذة", use_container_width=True, type="primary"):
            c_db['prioritized_teachers'] = prioritized
            c_db['no_first_slot_teachers'] = no_first_slot
            update_complex_state('constraints', c_db)
            st.success("تم الحفظ بنجاح!")

    # =======================================
    # التبويب 3: علاقات الأساتذة (المرافقة والتعارض)
    # =======================================
    with tab3:
        st.subheader("الارتباط والانفصال بين الأساتذة")
        col5, col6 = st.columns(2)
        
        # قيد المرافقة
        with col5:
            with st.container(border=True):
                st.write("**🚗 قيد المرافقة (اشتراك في الأيام):**")
                t1_car = st.selectbox("الأستاذ الأول:", st.session_state.db['teachers'], key="t1_car")
                t2_car = st.selectbox("الأستاذ الثاني:", st.session_state.db['teachers'], key="t2_car")
                if st.button("➕ إضافة قيد مرافقة", use_container_width=True):
                    if t1_car != t2_car:
                        pair = sorted([t1_car, t2_car])
                        if pair not in c_db['carpool_pairs']:
                            c_db['carpool_pairs'].append(pair)
                            update_complex_state('constraints', c_db)
                            st.rerun()
                
                st.markdown("---")
                for idx, pair in enumerate(c_db['carpool_pairs']):
                    p_c1, p_c2 = st.columns([4, 1])
                    p_c1.markdown(f"🤝 `{pair[0]}` يرافق `{pair[1]}`")
                    if p_c2.button("حذف", key=f"del_car_{idx}"):
                        c_db['carpool_pairs'].pop(idx)
                        update_complex_state('constraints', c_db)
                        st.rerun()

        # قيد عدم الاشتراك
        with col6:
            with st.container(border=True):
                st.write("**🏠 قيد الانفصال (عدم الاشتراك في الأيام):**")
                t1_con = st.selectbox("الأستاذ الأول:", st.session_state.db['teachers'], key="t1_con")
                t2_con = st.selectbox("الأستاذ الثاني:", st.session_state.db['teachers'], key="t2_con")
                if st.button("➕ إضافة قيد انفصال", use_container_width=True):
                    if t1_con != t2_con:
                        pair = sorted([t1_con, t2_con])
                        if pair not in c_db['conflict_pairs']:
                            c_db['conflict_pairs'].append(pair)
                            update_complex_state('constraints', c_db)
                            st.rerun()
                            
                st.markdown("---")
                for idx, pair in enumerate(c_db['conflict_pairs']):
                    p_c1, p_c2 = st.columns([4, 1])
                    p_c1.markdown(f"⚡ `{pair[0]}` عكس `{pair[1]}`")
                    if p_c2.button("حذف", key=f"del_con_{idx}"):
                        c_db['conflict_pairs'].pop(idx)
                        update_complex_state('constraints', c_db)
                        st.rerun()