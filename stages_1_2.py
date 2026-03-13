import streamlit as st
from data_manager import (
    add_teacher, remove_teacher, 
    add_room, remove_room, 
    add_level, remove_level, 
    add_subject, remove_subject,
    update_complex_state, execute_query,
    import_from_json, load_full_db # تمت إضافة دوال الاستيراد هنا
)

def render_stage1():
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 20px; padding: 15px; border: 2px solid #1c83e1; border-radius: 10px; background-color: rgba(28,131,225,0.1); font-weight: bold;'>
        1. إدخال البيانات
    </h2>
    """, unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("إدخال الأساتذة")
        with st.form("t_form", clear_on_submit=True):
            t_input = st.text_area("أسماء الأساتذة (اسم في كل سطر):", height=200)
            if st.form_submit_button("إضافة الأساتذة", use_container_width=True):
                if t_input:
                    new_t = list(dict.fromkeys([n.strip() for n in t_input.split('\n') if n.strip()]))
                    for t in new_t:
                        add_teacher(t)
                    st.success(f"تم إضافة {len(new_t)} أستاذ بنجاح.")
                    st.rerun()

    with col2:
        st.subheader("إدخال القاعات")
        with st.form("r_form", clear_on_submit=True):
            r_type = st.selectbox("نوع القاعة:", ["قاعة كبيرة", "قاعة متوسطة", "قاعة صغيرة"])
            r_input = st.text_area("أسماء القاعات (اسم في كل سطر):", height=145)
            if st.form_submit_button("إضافة القاعات", use_container_width=True):
                if r_input:
                    new_r = list(dict.fromkeys([n.strip() for n in r_input.split('\n') if n.strip()]))
                    for r in new_r:
                        add_room(r, r_type)
                    st.success(f"تم إضافة {len(new_r)} قاعة بنجاح.")
                    st.rerun()

    with col3:
        st.subheader("إدخال المستويات")
        with st.form("l_form", clear_on_submit=True):
            l_input = st.text_area("أسماء المستويات (اسم في كل سطر):", height=200)
            if st.form_submit_button("إضافة المستويات", use_container_width=True):
                if l_input:
                    new_l = list(dict.fromkeys([n.strip() for n in l_input.split('\n') if n.strip()]))
                    for l in new_l:
                        add_level(l)
                    st.success(f"تم إضافة {len(new_l)} مستوى بنجاح.")
                    st.rerun()

    with col4:
        st.subheader("إدخال المواد")
        if st.session_state.db['levels']:
            with st.form("s_form", clear_on_submit=True):
                s_level = st.selectbox("اختر المستوى:", st.session_state.db['levels'])
                s_input = st.text_area("أسماء المواد:", height=60)
                if st.form_submit_button("إضافة المواد", use_container_width=True):
                    if s_input and s_level:
                        new_s = list(dict.fromkeys([n.strip() for n in s_input.split('\n') if n.strip()]))
                        for sub in new_s:
                            add_subject(sub, s_level)
                        st.success(f"تم إضافة {len(new_s)} مادة بنجاح.")
                        st.rerun()
        else:
            st.info("أضف المستويات أولاً.")

    # ==========================================
    # قسم استيراد البيانات (الحل الجديد)
    # ==========================================
    st.divider()
    st.markdown("""
    <div style='background-color: rgba(28,131,225,0.05); padding: 20px; border-radius: 10px; border: 1px dashed #1c83e1;'>
        <h3 style='color: #1c83e1; margin-top: 0;'>📥 استيراد نسخة احتياطية (ملف JSON)</h3>
        <p>إذا كان لديك ملف بيانات محفوظ مسبقاً، يمكنك رفعه هنا لاستعادة جميع الجداول والقيود، وسيتم حفظها تلقائياً في قاعدة البيانات.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("اختر ملف data.json", type=['json'], label_visibility="collapsed")
    if uploaded_file is not None:
        if st.button("تأكيد الاستيراد واسترجاع البيانات", use_container_width=True, type="primary"):
            json_string = uploaded_file.getvalue().decode("utf-8")
            success, message = import_from_json(json_string)
            if success:
                st.success(message)
                st.session_state.db = load_full_db() # تحديث الواجهة بالبيانات الجديدة
                st.rerun()
            else:
                st.error(message)

def render_stage2():
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 20px; padding: 15px; border: 2px solid #1c83e1; border-radius: 10px; background-color: rgba(28,131,225,0.1); font-weight: bold;'>
        2. الحذف والتعديل
    </h2>
    """, unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.subheader("حذف أستاذ")
        if st.session_state.db['teachers']:
            t_del = st.selectbox("اختر للحذف:", st.session_state.db['teachers'], key="del_t")
            if st.button("حذف الأستاذ", use_container_width=True):
                from data_manager import remove_teacher, update_complex_state
                remove_teacher(t_del)
                
                # 1. تنظيف إسنادات المواد (المرحلة 3)
                ts_dict = st.session_state.db.get('teacher_subjects', {})
                if t_del in ts_dict:
                    del ts_dict[t_del]
                    update_complex_state('teacher_subjects', ts_dict)
                    
                # 2. 🌟 تنظيف القيود (المرحلة 6) 🌟
                constraints = st.session_state.db.get('constraints', {})
                modified_c = False
                
                if t_del in constraints.get('prioritized_teachers', []):
                    constraints['prioritized_teachers'].remove(t_del)
                    modified_c = True
                if t_del in constraints.get('no_first_slot_teachers', []):
                    constraints['no_first_slot_teachers'].remove(t_del)
                    modified_c = True
                    
                new_carpool = [pair for pair in constraints.get('carpool_pairs', []) if t_del not in pair]
                if len(new_carpool) != len(constraints.get('carpool_pairs', [])):
                    constraints['carpool_pairs'] = new_carpool
                    modified_c = True
                    
                new_conflict = [pair for pair in constraints.get('conflict_pairs', []) if t_del not in pair]
                if len(new_conflict) != len(constraints.get('conflict_pairs', [])):
                    constraints['conflict_pairs'] = new_conflict
                    modified_c = True
                    
                if modified_c:
                    update_complex_state('constraints', constraints)
                    
                st.rerun()

    with col2:
        st.subheader("حذف قاعة")
        if st.session_state.db['rooms']:
            r_del = st.selectbox("اختر للحذف:", list(st.session_state.db['rooms'].keys()), key="del_r")
            if st.button("حذف القاعة", use_container_width=True):
                from data_manager import remove_room, update_complex_state
                remove_room(r_del)
                
                # 🌟 تنظيف تخصيص القاعات (المرحلة 4) 🌟
                lr_dict = st.session_state.db.get('level_rooms', {})
                for lvl in lr_dict:
                    # إزالة القاعة سواء كانت بالاسم فقط أو بالاسم والنوع معاً
                    lr_dict[lvl] = [r for r in lr_dict[lvl] if not r.startswith(r_del)]
                update_complex_state('level_rooms', lr_dict)
                
                st.rerun()

    with col3:
        st.subheader("حذف مستوى")
        if st.session_state.db['levels']:
            l_del = st.selectbox("اختر للحذف:", st.session_state.db['levels'], key="del_l")
            if st.button("حذف المستوى", use_container_width=True):
                from data_manager import remove_level, execute_query, update_complex_state
                remove_level(l_del)
                execute_query("DELETE FROM subjects WHERE level = ?", (l_del,))
                
                # 1. تنظيف إسنادات الأساتذة (المرحلة 3)
                ts_dict = st.session_state.db.get('teacher_subjects', {})
                for t in ts_dict:
                    ts_dict[t] = [sub for sub in ts_dict[t] if not sub.endswith(f"({l_del})")]
                update_complex_state('teacher_subjects', ts_dict)
                
                # 2. تنظيف الأوقات (المرحلة 5)
                schedule = st.session_state.db.get('schedule', {})
                for day in schedule:
                    for slot in schedule[day]:
                        if l_del in slot.get('levels', []):
                            slot['levels'].remove(l_del)
                update_complex_state('schedule', schedule)
                
                # 3. تنظيف القيود التعارضية (المرحلة 6)
                constraints = st.session_state.db.get('constraints', {})
                incompatibles = constraints.get('incompatible_levels', [])
                new_incompatibles = [pair for pair in incompatibles if l_del not in pair]
                if len(new_incompatibles) != len(incompatibles):
                    constraints['incompatible_levels'] = new_incompatibles
                    update_complex_state('constraints', constraints)
                
                # 4. 🌟 تنظيف تخصيص القاعات (المرحلة 4) 🌟
                lr_dict = st.session_state.db.get('level_rooms', {})
                if l_del in lr_dict:
                    del lr_dict[l_del]
                    update_complex_state('level_rooms', lr_dict)
                    
                st.rerun()

    with col4:
        st.subheader("حذف مادة")
        if st.session_state.db['subjects']:
            levels_w_subs = list(set(s['level'] for s in st.session_state.db['subjects']))
            if levels_w_subs:
                l_for_s = st.selectbox("المستوى:", levels_w_subs, key="del_s_l")
                subs = [s['name'] for s in st.session_state.db['subjects'] if s['level'] == l_for_s]
                if subs:
                    s_del = st.selectbox("المادة:", subs, key="del_s")
                    if st.button("حذف المادة", use_container_width=True):
                        from data_manager import remove_subject, update_complex_state
                        remove_subject(s_del, l_for_s)
                        
                        # تنظيف إسنادات الأساتذة من هذه المادة فقط (المرحلة 3)
                        ts_dict = st.session_state.db.get('teacher_subjects', {})
                        target_sub = f"{s_del} ({l_for_s})"
                        for t in ts_dict:
                            if target_sub in ts_dict[t]:
                                ts_dict[t].remove(target_sub)
                        update_complex_state('teacher_subjects', ts_dict)
                        
                        st.rerun()

    st.divider()
    st.write("### معاينة البيانات المحفوظة:")
    c1, c2, c3, c4 = st.columns(4)
    c1.write(f"**الأساتذة:**")
    c1.json(st.session_state.db['teachers'])
    c2.write(f"**القاعات:**")
    c2.json(st.session_state.db['rooms'])
    c3.write(f"**المستويات:**")
    c3.json(st.session_state.db['levels'])
    
    c4.write(f"**المواد حسب المستوى:**")
    if st.session_state.db['subjects']:
        levels = list(set([s['level'] for s in st.session_state.db['subjects']]))
        for lvl in levels:
            c4.markdown(f"#### :blue[{lvl}]")
            lvl_subs = [s['name'] for s in st.session_state.db['subjects'] if s['level'] == lvl]
            for sub in lvl_subs:
                c4.markdown(f"- {sub}")
    else:
        c4.info("لا توجد مواد مسجلة حالياً.")