import streamlit as st
import pandas as pd

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="TuitionPulse - Multi-Owner Management",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INITIAL SESSION STATES ---
if "owners" not in st.session_state:
    st.session_state.owners = [{"name": "Default Admin", "phone": "9421517736", "password": "admin123"}]

if "students" not in st.session_state:
    st.session_state.students = []

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# --- SIDEBAR AUTHENTICATION & NAVIGATION ---
st.sidebar.title("⚡ TuitionPulse Access")

login_role = st.sidebar.selectbox("Choose Login Role:", ["Mentor / Owner", "Parent", "Operator Master"])

app_screen = "Welcome"

if login_role == "Mentor / Owner":
    st.sidebar.markdown("### Mentor Password Login")
    mentor_phone = st.sidebar.text_input("Mobile Number", placeholder="10-digit mobile number", key="mentor_phone_input")
    mentor_pass = st.sidebar.text_input("Password (Assigned by Operator)", type="password", key="mentor_pass_input")
    mentor_login_btn = st.sidebar.button("Login as Mentor")
    
    if mentor_login_btn:
        matched_owner = next((o for o in st.session_state.owners if o["phone"] == mentor_phone and o.get("password") == mentor_pass), None)
        if matched_owner:
            st.session_state.logged_in_user = {"role": "owner", "phone": mentor_phone}
            st.sidebar.success(f"Welcome back, {matched_owner['name']}!")
            app_screen = "Owner Panel"
        else:
            st.sidebar.error("Invalid mobile number or incorrect password.")
            app_screen = "Owner Login Prompt"
    else:
        if st.session_state.get("logged_in_user") and st.session_state.logged_in_user.get("role") == "owner":
            app_screen = "Owner Panel"
        else:
            app_screen = "Owner Login Prompt"

elif login_role == "Operator Master":
    st.sidebar.markdown("### Operator Master Access")
    op_code = st.sidebar.text_input("Operator Passcode", type="password", key="op_code_input")
    op_login_btn = st.sidebar.button("Login as Operator")
    
    if op_login_btn:
        if op_code == "OP123":  # Default Operator Passcode
            st.session_state.logged_in_user = {"role": "operator"}
            st.sidebar.success("Operator Access Granted!")
            app_screen = "Operator Dashboard"
        else:
            st.sidebar.error("Invalid Operator Passcode.")
            app_screen = "Operator Login Prompt"
    else:
        if st.session_state.get("logged_in_user") and st.session_state.logged_in_user.get("role") == "operator":
            app_screen = "Operator Dashboard"
        else:
            app_screen = "Operator Login Prompt"

else:
    st.sidebar.markdown("### Parent Sign-In")
    parent_phone = st.sidebar.text_input("Registered Parent Mobile", placeholder="10-digit mobile number", key="parent_phone_input")
    
    matched_students = [s for s in st.session_state.students if s["phone"] == parent_phone]
    if parent_phone:
        if matched_students:
            st.session_state.logged_in_user = {"role": "parent", "students": matched_students}
            st.sidebar.success(f"Verified! Found {len(matched_students)} child(ren).")
            app_screen = "Parent Portal View"
        else:
            st.sidebar.error("Mobile number not found in student records.")
            app_screen = "Parent Login Prompt"
    else:
        app_screen = "Parent Login Prompt"

# ================= LOGIN PROMPT & UNAUTHORIZED SCREENS =================
if app_screen == "Owner Login Prompt":
    st.title("⚡ TuitionPulse Owner Portal")
    st.info("👈 Please enter your registered 10-digit mobile number and operator-assigned password in the sidebar to log in.")
elif app_screen == "Operator Login Prompt":
    st.title("🛡️ TuitionPulse Operator Master Portal")
    st.info("👈 Please enter the secure operator passcode in the sidebar to manage system owners and mentors.")
elif app_screen == "Parent Login Prompt":
    st.title("⚡ TuitionPulse Parent Portal")
    st.info("👈 Please enter your registered 10-digit parent mobile number in the sidebar to access your children's data.")

# ================= OPERATOR MASTER DASHBOARD =================
elif app_screen == "Operator Dashboard":
    if not st.session_state.logged_in_user or st.session_state.logged_in_user.get("role") != "operator":
        st.session_state.logged_in_user = None
        st.rerun()
        
    st.title("🛡️ Master Operator Dashboard: Manage Owners & Passwords")
    st.info("As an operator, you can register new institute owners/mentors and assign their login passwords.")
    
    with st.form("add_owner_by_operator"):
        st.subheader("Add New Institute Owner / Mentor & Assign Password")
        col1, col2, col3 = st.columns(3)
        with col1:
            new_owner_name = st.text_input("Institute / Owner Name", placeholder="e.g. Success Coaching")
        with col2:
            new_owner_phone = st.text_input("10-Digit Mobile Number", placeholder="9876543210")
        with col3:
            new_owner_pass = st.text_input("Assign Password", type="password", placeholder="Secret login password")
            
        add_owner_submit = st.form_submit_button("Register Owner & Assign Password")
        if add_owner_submit:
            if new_owner_name and new_owner_phone and new_owner_pass and len(new_owner_phone) == 10:
                already_exists = any(o["phone"] == new_owner_phone for o in st.session_state.owners)
                if already_exists:
                    st.error("An owner with this mobile number already exists!")
                else:
                    st.session_state.owners.append({
                        "name": new_owner_name, 
                        "phone": new_owner_phone, 
                        "password": new_owner_pass
                    })
                    st.success(f"Registered owner '{new_owner_name}' successfully with assigned password!")
                    st.rerun()
            else:
                st.error("Please fill all fields with a valid 10-digit mobile number and password.")
                
    st.markdown("---")
    st.subheader("Currently Registered Owners & Mentors")
    if not st.session_state.owners:
        st.info("No owners registered.")
    else:
        for idx, o in enumerate(st.session_state.owners):
            cols = st.columns([3, 2, 2, 1])
            cols[0].write(f"**{o['name']}**")
            cols[1].write(f"Phone: +91 {o['phone']}")
            cols[2].write(f"Password: `{o.get('password', 'N/A')}`")
            if len(st.session_state.owners) > 1:
                if cols[3].button("Remove", key=f"rem_op_{idx}"):
                    st.session_state.owners.pop(idx)
                    st.warning(f"Removed owner {o['name']}")
                    st.rerun()
            else:
                cols[3].write("Primary Admin")

# ================= OWNER PANEL (FULL CONTROL & CUSTOMIZATION) =================
elif app_screen == "Owner Panel":
    current_phone = st.session_state.logged_in_user["phone"]
    owner_info = next((o for o in st.session_state.owners if o["phone"] == current_phone), None)
    
    if not owner_info:
        st.session_state.logged_in_user = None
        st.rerun()
        
    st.title(f"👑 Owner Dashboard: {owner_info['name']}")
    
    admin_tab = st.sidebar.radio(
        "Admin Menu:",
        ["1. Add & Manage Students 👨‍🎓", "2. Fees & Collections 💰", "3. Daily Attendance 📅", "4. Weekly Test Ranks 🏆", "5. Owner Profile & Settings ⚙️"]
    )
    
    # --- TAB 1: ADD, EDIT, CUSTOMIZE & REMOVE STUDENTS ---
    if admin_tab == "1. Add & Manage Students 👨‍🎓":
        st.subheader("Add New Student")
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                s_name = st.text_input("Student Name")
                roll_no = st.text_input("Roll Number / ID", value=f"100{len(st.session_state.students)+1}")
                parent_name = st.text_input("Parent Name")
            with col2:
                phone_no = st.text_input("Parent Mobile Number (For Parent Login)", placeholder="9876543210")
                fee_amount = st.number_input("Custom Monthly Fee (₹)", value=3500)
                
            submitted = st.form_submit_button("Add Student")
            if submitted:
                if s_name and phone_no and len(phone_no) == 10:
                    new_student = {
                        "id": f"s_{len(st.session_state.students)+1}",
                        "name": s_name,
                        "rollNo": roll_no,
                        "parentName": parent_name,
                        "phone": phone_no,
                        "amountDue": fee_amount,
                        "attendance": "P",
                        "marks": 0,
                        "rank": len(st.session_state.students) + 1,
                        "homeworkStatus": "Assigned"
                    }
                    st.session_state.students.append(new_student)
                    st.success(f"Added {s_name} successfully!")
                    st.rerun()
                else:
                    st.error("Please provide a valid student name and 10-digit mobile number.")

        st.markdown("---")
        st.subheader("Manage, Customize & Remove Existing Students")
        if not st.session_state.students:
            st.info("No students added yet.")
        else:
            for s in st.session_state.students:
                with st.expander(f"🎓 {s['name']} (Roll: #{s['rollNo']}) - Edit / Remove"):
                    with st.form(key=f"edit_form_{s['id']}"):
                        new_name = st.text_input("Student Name", value=s['name'], key=f"n_{s['id']}")
                        new_parent = st.text_input("Parent Name", value=s['parentName'], key=f"pn_{s['id']}")
                        new_phone = st.text_input("Parent Mobile Number", value=s['phone'], key=f"ph_{s['id']}")
                        new_fee = st.number_input("Custom Monthly Fee (₹)", value=s['amountDue'], key=f"fee_{s['id']}")
                        
                        col_save, col_del = st.columns(2)
                        save_update = col_save.form_submit_button("💾 Save Changes")
                        delete_student = col_del.form_submit_button("🗑️ Remove Student")
                        
                        if save_update:
                            s['name'] = new_name
                            s['parentName'] = new_parent
                            s['phone'] = new_phone
                            s['amountDue'] = new_fee
                            st.success(f"Updated details for {new_name}!")
                            st.rerun()
                            
                        if delete_student:
                            st.session_state.students.remove(s)
                            st.warning(f"Removed {s['name']} from database.")
                            st.rerun()

    # --- TAB 2: FEES & COLLECTIONS (AUTOMATED WHATSAPP REMINDERS) ---
    elif admin_tab == "2. Fees & Collections 💰":
        st.subheader("Fee Collection & Automated WhatsApp Reminders")
        if not st.session_state.students:
            st.info("No students registered yet.")
        else:
            overdue = [s for s in st.session_state.students if s["amountDue"] > 0]
            st.metric("Total Outstanding Fees", f"₹{sum(s['amountDue'] for s in overdue):,}")
            
            for s in st.session_state.students:
                with st.expander(f"{s['name']} - ₹{s['amountDue']} Due"):
                    wa_message = f"Dear%20{s['parentName']},%20this%20is%20an%20automated%20reminder%20that%20the%20fee%20of%20₹{s['amountDue']}%20for%20{s['name']}%20is%20due.%20Please%20clear%20it%20at%20your%20earliest.%20-TuitionPulse"
                    wa_url = f"https://wa.me/91{s['phone']}?text={wa_message}"
                    
                    st.link_button(f"💬 Send Automated WhatsApp Reminder to {s['parentName']}", url=wa_url)
                    
                    if s["amountDue"] > 0 and st.button("Mark Paid", key=f"paid_{s['id']}"):
                        s["amountDue"] = 0
                        st.success("Marked as paid!")
                        st.rerun()

    # --- TAB 3: DAILY ATTENDANCE (AUTOMATED ABSENT WHATSAPP ALERTS) ---
    elif admin_tab == "3. Daily Attendance 📅":
        st.subheader("Daily Attendance Tracker & Automated Alerts")
        if not st.session_state.students:
            st.info("No students registered yet.")
        else:
            for s in st.session_state.students:
                cols = st.columns([3, 1, 1, 1])
                cols[0].write(f"**{s['name']}**")
                if cols[1].button("Present", key=f"p_{s['id']}"):
                    s["attendance"] = "P"
                if cols[2].button("Absent 🚨", key=f"a_{s['id']}"):
                    s["attendance"] = "A"
                cols[3].write(f"Status: **{s['attendance']}**")
                
                if s["attendance"] == "A":
                    absent_msg = f"Dear%20{s['parentName']},%20automated%20alert:%20Your%20child%20{s['name']}%20is%20marked%20ABSENT%20from%20tuition%20today.%20-TuitionPulse"
                    absent_wa_url = f"https://wa.me/91{s['phone']}?text={absent_msg}"
                    st.link_button(f"📲 Send Automated WhatsApp Absent Alert to {s['parentName']}", url=absent_wa_url)

    # --- TAB 4: WEEKLY TEST RANKS ---
    elif admin_tab == "4. Weekly Test Ranks 🏆":
        st.subheader("Test Marks & Ranking")
        if not st.session_state.students:
            st.info("No students registered yet.")
        else:
            sorted_studs = sorted(st.session_state.students, key=lambda x: x["marks"], reverse=True)
            for idx, s in enumerate(sorted_studs):
                s["rank"] = idx + 1
                cols = st.columns([1, 3, 2])
                cols[0].markdown(f"### #{s['rank']}")
                cols[1].write(f"**{s['name']}**")
                new_marks = cols[2].number_input("Marks", value=s["marks"], key=f"m_{s['id']}")
                if new_marks != s["marks"]:
                    s["marks"] = new_marks
                    st.rerun()

    # --- TAB 5: OWNER PROFILE & SETTINGS (AUTO-LOGOUT ON CHANGE) ---
    elif admin_tab == "5. Owner Profile & Settings ⚙️":
        st.subheader("Owner Profile & Credentials")
        st.info("💡 Changing your owner mobile number, password, or profile details will automatically log you out for security.")
        
        with st.form("owner_settings_form"):
            updated_name = st.text_input("Institute / Owner Name", value=owner_info['name'])
            updated_phone = st.text_input("Owner Mobile Number (Login ID)", value=owner_info['phone'])
            updated_pass = st.text_input("Owner Password", type="password", value=owner_info.get('password', ''))
            
            update_btn = st.form_submit_button("Update Credentials & Logout")
            if update_btn:
                if updated_name and updated_pass and len(updated_phone) == 10:
                    owner_info['name'] = updated_name
                    owner_info['phone'] = updated_phone
                    owner_info['password'] = updated_pass
                    st.success("Credentials updated! Logging out automatically...")
                    st.session_state.logged_in_user = None
                    st.rerun()
                else:
                    st.error("Please provide a valid name, password, and 10-digit phone number.")

# ================= PARENT PORTAL VIEW (SUPPORTS MULTIPLE CHILDREN) =================
elif app_screen == "Parent Portal View":
    children = st.session_state.logged_in_user["students"]
    st.subheader("📱 Parent Portal: Children Dashboard")
    
    if len(children) == 1:
        child = children[0]
        st.markdown(f"### Child Profile: {child['name']}")
        col1, col2 = st.columns(2)
        col1.metric("Today's Attendance", "Present ✅" if child["attendance"] == "P" else "Absent 🚨")
        col2.metric("Weekly Class Rank", f"#{child['rank']}", f"Score: {child['marks']}")
        
        st.info(f"**Assigned Homework:** {child['homeworkStatus']}")
        
        st.markdown("### Tuition Fee Status")
        if child["amountDue"] > 0:
            st.error(f"Pending Dues: ₹{child['amountDue']:,}")
            if st.button("💳 Pay via UPI QR", key=f"pay_{child['id']}"):
                child["amountDue"] = 0
                st.success("🎉 Payment received successfully! Dues cleared.")
                st.rerun()
        else:
            st.success("✅ Fee fully paid for this month.")
            
    else:
        child_tabs = st.tabs([f"🎓 {c['name']} (Roll: #{c['rollNo']})" for c in children])
        
        for idx, tab in enumerate(child_tabs):
            with tab:
                child = children[idx]
                st.markdown(f"### Dashboard for {child['name']}")
                
                col1, col2 = st.columns(2)
                col1.metric("Today's Attendance", "Present ✅" if child["attendance"] == "P" else "Absent 🚨", key=f"att_{child['id']}")
                col2.metric("Weekly Class Rank", f"#{child['rank']}", f"Score: {child['marks']}", key=f"rk_{child['id']}")
                
                st.info(f"**Assigned Homework:** {child['homeworkStatus']}")
                
                st.markdown("### Tuition Fee Status")
                if child["amountDue"] > 0:
                    st.error(f"Pending Dues: ₹{child['amountDue']:,}")
                    if st.button("💳 Pay via UPI QR", key=f"pay_multi_{child['id']}"):
                        child["amountDue"] = 0
                        st.success("🎉 Payment received successfully! Dues cleared.")
                        st.rerun()
                else:
                    st.success("✅ Fee fully paid for this month.")