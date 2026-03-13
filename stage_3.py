import streamlit as st
from data_manager import update_complex_state
from st_keyup import st_keyup

def render_stage3():
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 20px; padding: 15px; border: 2px solid #1c83e1; border-radius: 10px; background-color: rgba(28,131,225,0.1); font-weight: bold;'>
        3. إسناد المواد للأساتذة
    </h2>
    """, unsafe_allow_html=True)
    
    if not st.session_state.db['teachers'] or not st.session_state.db['subjects']:
        st.warning("⚠️ يرجى إدخال الأساتذة والمواد في المرحلة الأولى أولاً.")
        return

    # خريطة لمعرفة كل مادة لمن هي مسندة (لغرض التلوين والتوضيح)
    subject_to_teacher = {}
    for t, subs in st.session_state.db.get('teacher_subjects', {}).items():
        for s in subs:
            if s not in subject_to_teacher:
                subject_to_teacher[s] = []
            subject_to_teacher[s].append(t)

    col1, col2 = st.columns(2)
    
    # =======================================
    # العمود الأول: قائمة الأساتذة (مع البحث)
    # =======================================
    with col1:
        st.subheader("👨‍🏫 1. اختر الأستاذ")
        
        search_t = st_keyup("🔍 بحث عن أستاذ:", placeholder="اكتب اسم الأستاذ...", key="search_t_s3")
        if search_t is None: search_t = ""
        filtered_teachers = [t for t in st.session_state.db['teachers'] if search_t.lower() in t.lower()]
        
        def format_teacher(t):
            if st.session_state.db.get('teacher_subjects', {}).get(t):
                return f"✅ {t}" 
            return t
            
        with st.container(height=400, border=True):
            if filtered_teachers:
                selected_teacher = st.radio(
                    "الأساتذة:", 
                    options=filtered_teachers, 
                    format_func=format_teacher,
                    label_visibility="collapsed",
                    key="s3_teacher_radio" 
                )
            else:
                st.info("لا يوجد أستاذ بهذا الاسم.")
                selected_teacher = None
            
        if selected_teacher:
            current_subs = st.session_state.db.get('teacher_subjects', {}).get(selected_teacher, [])
            if current_subs:
                with st.expander(f"👀 عرض المواد المسندة لـ ({selected_teacher})", expanded=True):
                    # 🌟 التعديل الجديد: إضافة زر حذف لكل مادة 🌟
                    for s in current_subs:
                        c_sub, c_btn = st.columns([5, 1])
                        c_sub.markdown(f"- {s}")
                        if c_btn.button("❌", key=f"del_one_sub_{selected_teacher}_{s}", help="إلغاء إسناد هذه المادة فقط"):
                            ts_dict = st.session_state.db.get('teacher_subjects', {})
                            ts_dict[selected_teacher].remove(s)
                            update_complex_state('teacher_subjects', ts_dict)
                            # إجبار القائمة اليمنى (Checkboxes) على التحديث
                            if 'draft_t_s3' in st.session_state:
                                del st.session_state['draft_t_s3'] 
                            st.rerun()
                            
                    st.markdown("---")
                    if st.button("🗑️ إفراغ كل مواده", key=f"clear_{selected_teacher}", use_container_width=True):
                        ts_dict = st.session_state.db.get('teacher_subjects', {})
                        ts_dict[selected_teacher] = []
                        update_complex_state('teacher_subjects', ts_dict)
                        # إجبار القائمة اليمنى على التحديث
                        if 'draft_t_s3' in st.session_state:
                            del st.session_state['draft_t_s3'] 
                        st.rerun()

    # =======================================
    # العمود الثاني: قائمة المواد (مع البحث)
    # =======================================
    with col2:
        st.subheader("📚 2. حدد مواده")
        
        if selected_teacher:
            st.write(f"المواد المختارة ستُسند للأستاذ: **:blue[{selected_teacher}]**")
            
            search_s = st_keyup("🔍 بحث عن مادة:", placeholder="اكتب اسم المادة...", key="search_s_s3")
            if search_s is None: search_s = ""
            
            formatted_subjects = [f"{s['name']} ({s['level']})" for s in st.session_state.db['subjects']]
            
            if 'draft_t_s3' not in st.session_state or st.session_state.draft_t_s3 != selected_teacher:
                st.session_state.draft_t_s3 = selected_teacher
                st.session_state.draft_subs_s3 = st.session_state.db.get('teacher_subjects', {}).get(selected_teacher, []).copy()

            def update_draft(sub_val):
                is_checked = st.session_state[f"chk_s3_{sub_val}_{selected_teacher}"]
                if is_checked and sub_val not in st.session_state.draft_subs_s3:
                    st.session_state.draft_subs_s3.append(sub_val)
                elif not is_checked and sub_val in st.session_state.draft_subs_s3:
                    st.session_state.draft_subs_s3.remove(sub_val)

            filtered_subjects = [s for s in formatted_subjects if search_s.lower() in s.lower()]
            
            with st.container(height=400, border=True):
                if filtered_subjects:
                    for sub in filtered_subjects:
                        is_checked = sub in st.session_state.draft_subs_s3
                        
                        if sub in subject_to_teacher:
                            owners = "، ".join(subject_to_teacher[sub])
                            display_label = f"✅ :green[{sub}] (عند: {owners})"
                        else:
                            display_label = sub
                            
                        st.checkbox(
                            display_label, 
                            value=is_checked, 
                            key=f"chk_s3_{sub}_{selected_teacher}",
                            on_change=update_draft,
                            args=(sub,)
                        )
                else:
                    st.info("لا توجد مادة بهذا الاسم.")
        else:
            st.info("يرجى اختيار أستاذ من القائمة أولاً.")
                    
    # =======================================
    # زر التخصيص
    # =======================================
    st.markdown("<br>", unsafe_allow_html=True)
    if selected_teacher:
        if st.button("💾 تخصيص / تحديث الإسناد", type="primary", use_container_width=True):
            ts_dict = st.session_state.db.get('teacher_subjects', {})
            ts_dict[selected_teacher] = st.session_state.draft_subs_s3.copy()
            update_complex_state('teacher_subjects', ts_dict)
            st.success(f"تم إسناد المواد للأستاذ {selected_teacher} بنجاح!")
            if 'draft_t_s3' in st.session_state:
                del st.session_state['draft_t_s3']
            st.rerun()