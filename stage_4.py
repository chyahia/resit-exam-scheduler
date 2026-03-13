import streamlit as st
from data_manager import update_complex_state

def render_stage4():
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 20px; padding: 15px; border: 2px solid #1c83e1; border-radius: 10px; background-color: rgba(28,131,225,0.1); font-weight: bold;'>
        4. تخصيص القاعات
    </h2>
    """, unsafe_allow_html=True)
    
    # التحقق من وجود بيانات
    if not st.session_state.db['levels'] or not st.session_state.db['rooms']:
        st.warning("⚠️ يرجى إدخال المستويات والقاعات في المرحلة الأولى أولاً.")
        return

    st.write("قم بالتأشير على القاعات المخصصة لكل مستوى، ثم اضغط على زر الحفظ في الأسفل.")
    st.markdown("<br>", unsafe_allow_html=True)

    # تجهيز قائمة القاعات مع أنواعها
    formatted_rooms = [f"{r_name} ({r_type})" for r_name, r_type in st.session_state.db['rooms'].items()]
    
    # عناوين الأعمدة
    header_col1, header_col2 = st.columns([1, 4])
    with header_col1:
        st.markdown("### 📚 المستويات")
    with header_col2:
        st.markdown("### 🏫 القاعات المتاحة")
    st.divider()

    # قاموس مؤقت لحفظ التحديدات قبل ضغط زر الحفظ
    current_selections = {}

    # إنشاء صف لكل مستوى
    for level in st.session_state.db['levels']:
        # عمود صغير للمستوى، وعمود كبير للقاعات
        col1, col2 = st.columns([1, 4])
        
        with col1:
            # عرض اسم المستوى بشكل بارز
            st.markdown(f"#### :blue[{level}]")
            
        with col2:
            # تقسيم مساحة القاعات إلى 4 أعمدة لتظهر كشبكة (صفوف متجاورة)
            chk_cols = st.columns(4)
            
            # جلب القاعات المحفوظة مسبقاً لهذا المستوى لتكون مؤشرة
            saved_rooms = st.session_state.db['level_rooms'].get(level, [])
            
            selected_for_this_level = []
            
            # عرض مربعات التأشير (Checkboxes) وتوزيعها على الأعمدة الأربعة
            for idx, room in enumerate(formatted_rooms):
                # نستخدم idx % 4 لتوزيع القاعات بالتساوي على الأعمدة الأربعة
                is_checked = chk_cols[idx % 4].checkbox(
                    room, 
                    value=(room in saved_rooms), 
                    key=f"chk_s4_{level}_{room}"
                )
                if is_checked:
                    selected_for_this_level.append(room)
            
            current_selections[level] = selected_for_this_level
            
        # خط فاصل بين كل مستوى والذي يليه
        st.markdown("---")

    # زر الحفظ في الأسفل
    if st.button("💾 حفظ تخصيص القاعات لجميع المستويات", type="primary", use_container_width=True):
        # تحديث قاعدة البيانات
        update_complex_state('level_rooms', current_selections)
        st.success("تم حفظ تخصيص القاعات بنجاح!")
        st.rerun()

    # ==========================================
    # المعاينة (اختياري، لكنه مفيد للتأكد)
    # ==========================================
    st.divider()
    st.write("### معاينة القاعات المخصصة:")
    
    has_room_assignments = any(len(rooms) > 0 for rooms in st.session_state.db.get('level_rooms', {}).values())
    
    if has_room_assignments:
        cols = st.columns(3)
        col_idx = 0
        for level, rooms in st.session_state.db.get('level_rooms', {}).items():
            if rooms:
                with cols[col_idx].expander(f"📚 {level} ({len(rooms)} قاعات)", expanded=True):
                    for r in rooms:
                        st.markdown(f"- {r}")
                col_idx = (col_idx + 1) % 3
    else:
        st.info("لم يتم تخصيص أي قاعات لأي مستوى حتى الآن.")