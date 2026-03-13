import streamlit as st
from data_manager import update_complex_state
import datetime

# قاموس لتحويل أرقام الأيام إلى أسماء عربية
ARABIC_DAYS = {6: "الأحد", 0: "الإثنين", 1: "الثلاثاء", 2: "الأربعاء", 3: "الخميس", 4: "الجمعة", 5: "السبت"}

def render_stage5():
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 20px; padding: 15px; border: 2px solid #1c83e1; border-radius: 10px; background-color: rgba(28,131,225,0.1); font-weight: bold;'>
        5. أيام وأوقات الامتحان
    </h2>
    """, unsafe_allow_html=True)
    
    if not st.session_state.db['levels']:
        st.warning("⚠️ يرجى إدخال المستويات في المرحلة الأولى أولاً لتتمكن من وضع الجدول.")
        return

    # ==========================================
    # 1. إضافة يوم جديد باستخدام التقويم
    # ==========================================
    st.subheader("إضافة يوم امتحان")
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_date = st.date_input("اختر تاريخ الامتحان:", key="new_date_sel_s5")
        day_name = ARABIC_DAYS[selected_date.weekday()]
        new_day = f"{day_name} ({selected_date.strftime('%Y-%m-%d')})"
        
        is_valid = True
        if new_day in st.session_state.db['schedule']:
            st.warning("⚠️ لقد قمت بإضافة هذا التاريخ مسبقاً.")
            is_valid = False
            
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ إضافة اليوم", use_container_width=True, disabled=not is_valid, type="primary"):
            st.session_state.db['schedule'][new_day] = [] 
            update_complex_state('schedule', st.session_state.db['schedule'])
            st.rerun()

    st.divider()

    # ==========================================
    # 2. عرض الأيام المضافة (على شكل تبويبات)
    # ==========================================
    days_list = list(st.session_state.db['schedule'].keys())
    
    if not days_list:
        st.info("لم يتم إضافة أي أيام بعد. ابدأ باختيار تاريخ من التقويم في الأعلى.")
        return

    st.subheader("إدارة الأيام والأوقات")
    
    # إنشاء التبويبات بناءً على الأيام المضافة
    tabs = st.tabs(days_list)
    
    # المرور على كل يوم والتبويب الخاص به
    for day, tab in zip(days_list, tabs):
        with tab:
            # شريط التحكم الخاص باليوم (تكرار وحذف)
            ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
            with ctrl_col2:
                with st.popover("🔄 تكرار هذا اليوم"):
                    st.write("نسخ نفس أوقات ومستويات هذا اليوم إلى تاريخ آخر:")
                    target_date = st.date_input("اختر التاريخ الجديد:", key=f"dup_date_{day}")
                    
                    target_day_name = ARABIC_DAYS[target_date.weekday()]
                    target_day = f"{target_day_name} ({target_date.strftime('%Y-%m-%d')})"
                    
                    if target_day in st.session_state.db['schedule']:
                        st.error("هذا التاريخ موجود مسبقاً!")
                    else:
                        if st.button("تأكيد النسخ", key=f"btn_dup_{day}", use_container_width=True):
                            import copy
                            st.session_state.db['schedule'][target_day] = copy.deepcopy(st.session_state.db['schedule'][day])
                            update_complex_state('schedule', st.session_state.db['schedule'])
                            st.success("تم النسخ!")
                            st.rerun()
            with ctrl_col3:
                if st.button("🗑️ حذف هذا اليوم", key=f"del_day_{day}", use_container_width=True):
                    del st.session_state.db['schedule'][day]
                    update_complex_state('schedule', st.session_state.db['schedule'])
                    st.rerun()

            st.markdown("---")

            # ==========================================
            # إضافة وإدارة أوقات الامتحان داخل هذا التبويب
            # ==========================================
            st.markdown(f"**إضافة وقت امتحان جديد ليوم {day}:**")
            t_col1, t_col2 = st.columns([3, 1])
            with t_col1:
                new_time = st.text_input(f"الوقت (مثال: من 8:30 إلى 10:00)", key=f"time_in_{day}")
            with t_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("➕ إضافة الوقت", key=f"add_time_{day}", use_container_width=True):
                    if new_time:
                        st.session_state.db['schedule'][day].append({"time": new_time, "levels": []})
                        update_complex_state('schedule', st.session_state.db['schedule'])
                        st.rerun()

            # عرض الأوقات المضافة داخل اليوم
            slots = st.session_state.db['schedule'][day]
            if slots:
                st.markdown("#### الأوقات المحددة والمستويات المعنية:")
                for idx, slot in enumerate(slots):
                    with st.container(border=True):
                        s_col1, s_col2 = st.columns([4, 1])
                        with s_col1:
                            st.markdown(f"**⏰ الوقت: :blue[{slot['time']}]**")
                        with s_col2:
                            if st.button("🗑️ حذف الوقت", key=f"del_time_{day}_{idx}", use_container_width=True):
                                st.session_state.db['schedule'][day].pop(idx)
                                update_complex_state('schedule', st.session_state.db['schedule'])
                                st.rerun()

                        st.write("أشر على المستويات المعنية بهذا الوقت:")
                        l_cols = st.columns(4)
                        for l_idx, level in enumerate(st.session_state.db['levels']):
                            is_checked = level in slot['levels']
                            checked_now = l_cols[l_idx % 4].checkbox(level, value=is_checked, key=f"chk_lvl_{day}_{idx}_{level}")
                            
                            if checked_now and level not in slot['levels']:
                                slot['levels'].append(level)
                                update_complex_state('schedule', st.session_state.db['schedule'])
                            elif not checked_now and level in slot['levels']:
                                slot['levels'].remove(level)
                                update_complex_state('schedule', st.session_state.db['schedule'])