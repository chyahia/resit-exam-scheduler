import streamlit as st
import time
from solver import run_distribution
from exporter import generate_levels_word, generate_teachers_word

def render_stage7():
    st.markdown("""
    <h2 style='text-align: center; margin-bottom: 20px; padding: 15px; border: 2px solid #1c83e1; border-radius: 10px; background-color: rgba(28,131,225,0.1); font-weight: bold;'>
        7. التوزيع الذكي والتصدير
    </h2>
    """, unsafe_allow_html=True)
    
    with st.container(border=True):
        algo_choice = st.radio(
            "🧠 اختر نوع الخوارزمية:",
            options=["خوارزمية المسار الواحد (سريعة جداً)", "خوارزمية LNS للبحث العميق (الخيار الموصى به)"],
            index=1,
            horizontal=True
        )
        
        st.markdown("---")
        
        # 🌟 التعديل الجديد: خيارات استراتيجية التوزيع 🌟
        st.markdown("**🎯 استراتيجية التوزيع (عند تعارض الأهداف):**")
        strategy_choice = st.radio(
            "الأولوية لمن؟",
            options=[
                "👨‍🏫 تفضيل تجميع مواد الأستاذ (في نفس الحصة واليوم قدر الإمكان)", 
                "🎓 تفضيل تفادي تشتت الطلبة (فترات متتالية للمستوى مع محاولة حفظ أيام الأستاذ)"
            ],
            index=1, # الافتراضي هو تفادي التشتت
            horizontal=False
        )
        is_teacher_focused = "تجميع مواد الأستاذ" in strategy_choice
        
        is_lns = "LNS" in algo_choice
        if is_lns:
            st.markdown("---")
            st.markdown("**⚙️ إعدادات محرك LNS المتقدمة:**")
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                lns_duration = st.number_input("⏱️ مدة البحث العميق (بالثواني):", min_value=1, max_value=300, value=15, step=1)
            with col_s2:
                lns_destruction = st.number_input("💣 نسبة التدمير (Destruction Rate %):", min_value=5, max_value=90, value=25, step=5)
        else:
            lns_duration = 0
            lns_destruction = 0

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 بدء التوزيع وبناء الجداول", type="primary", use_container_width=True):
        if not st.session_state.db.get('schedule'):
            st.error("❌ لا يمكن البدء: جدول الأيام والأوقات فارغ.")
            return

        if is_lns:
            st.markdown("### 📊 المراقبة الحية لعمل الخوارزمية")
            progress_bar = st.progress(0.0)
            
            m_col1, m_col2, m_col3 = st.columns(3)
            ui_time = m_col1.empty()
            ui_hard = m_col2.empty()
            ui_soft = m_col3.empty()
            
            def live_update(elapsed, total, hard_v, soft_v):
                pct = min(elapsed / total, 1.0)
                progress_bar.progress(pct)
                rem = max(int(total - elapsed), 0)
                
                ui_time.metric("⏳ الوقت المتبقي", f"{rem} ثانية")
                ui_hard.metric("❌ قيود صارمة منتهكة", hard_v)
                ui_soft.metric("⚠️ قيود مرنة منتهكة", soft_v)
                
                time.sleep(0.05) 
        else:
            live_update = None
            st.info("⚡ جاري التوزيع السريع...")

        # 🌟 تمرير الخيار الجديد للخوارزمية 🌟
        schedule, violations = run_distribution(
            st.session_state.db, 
            use_lns=is_lns, 
            duration=lns_duration, 
            destruction_rate=lns_destruction,
            progress_callback=live_update,
            is_teacher_focused=is_teacher_focused
        )
        
        st.session_state.final_schedule = schedule
        st.session_state.violations = violations
        st.session_state.is_generated = True
        st.rerun()

    st.divider()

    if st.session_state.get('is_generated', False) and 'final_schedule' in st.session_state:
        
        violations = st.session_state.get('violations', [])
        if violations:
            st.error(f"⚠️ انتهى التوزيع مع وجود ({len(violations)}) قيود لم تتحقق (المرنة والصارمة):")
            with st.expander("🔻 عرض تقرير الانتهاكات", expanded=True):
                for v in violations:
                    st.write(v)
        else:
            st.success("✨ اكتمل التوزيع بمثالية! 100% من القيود محققة وتوقفت الخوارزمية بنجاح.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.write("### 📥 تصدير الجداول بصيغة Word")
        col1, col2 = st.columns(2)
        mem_levels = generate_levels_word(st.session_state.db, st.session_state.final_schedule)
        mem_teachers = generate_teachers_word(st.session_state.db, st.session_state.final_schedule)
        
        with col1:
            st.download_button("📄 تحميل جداول المستويات", mem_levels, "جداول_المستويات_استدراكي.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
        with col2:
            st.download_button("👨‍🏫 تحميل جداول الأساتذة", mem_teachers, "جداول_الأساتذة_استدراكي.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)