import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# -------------- SETTINGS --------------
currency = "RM"
page_title = "AD HCare Worker Management"
page_icon = "🙎‍♂️"  # emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"
# ------------------------------------
st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)
# Initialize database
conn = sqlite3.connect('worker_management.db', check_same_thread=False)
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS workers
             (id INTEGER PRIMARY KEY, name TEXT, join_date DATE, gender TEXT, phone TEXT,
              passport_number TEXT, passport_expiry DATE, visa_expiry DATE,
              company_name TEXT, address TEXT, state TEXT, pic_details TEXT,
              company_join_date DATE, base_salary REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS transactions
             (id INTEGER PRIMARY KEY, worker_id INTEGER, date DATE, amount REAL, 
              transaction_type TEXT)''')

conn.commit()

# Helper functions
def add_worker(name, join_date, gender, phone, passport_number, passport_expiry, visa_expiry,
               company_name, address, state, pic_details, company_join_date, base_salary):
    c.execute('''INSERT INTO workers (name, join_date, gender, phone, passport_number, 
                 passport_expiry, visa_expiry, company_name, address, state, pic_details, 
                 company_join_date, base_salary) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
              (name, join_date, gender, phone, passport_number, passport_expiry, visa_expiry,
               company_name, address, state, pic_details, company_join_date, base_salary))
    conn.commit()

def update_worker(worker_id, name, join_date, gender, phone, passport_number, passport_expiry, visa_expiry,
                  company_name, address, state, pic_details, company_join_date, base_salary):
    
    query = "UPDATE workers SET name=?, join_date=?, gender=?, phone=?, passport_number=?,passport_expiry=?, visa_expiry=?, company_name=?, address=?, state=?, pic_details=?, company_join_date=?, base_salary=? WHERE id= ?"
    c.execute(query, 
              (name, join_date, gender, phone, passport_number, passport_expiry, visa_expiry,
               company_name, address, state, pic_details, company_join_date, base_salary, str(worker_id)))
    conn.commit()

def delete_worker(worker_id):
    c.execute('DELETE FROM workers WHERE id=?', (str(worker_id),))
    c.execute('DELETE FROM transactions WHERE worker_id=?', (worker_id,))
    conn.commit()

def add_transaction(worker_id, date, amount, transaction_type):
    c.execute('''INSERT INTO transactions (worker_id, date, amount, transaction_type) 
                 VALUES (?, ?, ?, ?)''', (worker_id, date, amount, transaction_type))
    conn.commit()

def get_workers():
    return pd.read_sql_query("SELECT * FROM workers", conn)

def get_worker(worker_id):
    conn = sqlite3.connect('worker_management.db')
    query = "SELECT * FROM workers WHERE id =" + str(worker_id)
    df = pd.read_sql_query(query, conn)
    return df.iloc[0] if not df.empty else None

def get_transactions(worker_id=None, year=None, month=None):
    query = "SELECT * FROM transactions"
    params = []
    if worker_id:
        query += " WHERE worker_id=?"
        params.append(str(worker_id))
        if year and month:
            query += " AND strftime('%Y', date) = ? AND strftime('%m', date) = ?"
            params.extend([str(year), str(month).zfill(2)])
    return pd.read_sql_query(query, conn, params=params)

def get_total_paid_out():
    query = "SELECT SUM(amount) AS total FROM transactions WHERE strftime('%Y', date) = strftime('%Y', 'now') AND strftime('%m', date) = strftime('%m', 'now')"
    df = pd.read_sql_query(query, conn)
    return df['total'].iloc[0] if df['total'].notna().iloc[0] else 0

def get_earliest_transaction_year():
    df = pd.read_sql_query("SELECT MIN(strftime('%Y', date)) as earliest_year FROM transactions", conn)
    return int(df['earliest_year'].iloc[0]) if df['earliest_year'].notna().iloc[0] else datetime.now().year

# Streamlit app
def main():
    
    

    menu = ["🏠 Home", "👨‍🦱 Add Worker Info", "⚙️ Update Worker Info", "Delete Worker", "👀 View Workers Info", "💵 Transactions", "📊 Report"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "🏠 Home":
        col1, col2, col3 = st.columns(3)
        
        workers_df = get_workers()
        total_workers = len(workers_df)
        total_salary = workers_df['base_salary'].sum()
        total_paid_out = get_total_paid_out()
        
        with col1:
            st.metric("Number of Workers", total_workers, "Working with AD HCARE")
        
        with col2:
            st.metric("Total Salary", f"RM {total_salary:.2f}", "For All Workers")
        
        with col3:
            current_month = datetime.now().strftime("%B,%Y")
            st.metric("Paid Out", f"RM {total_paid_out:.2f}", f"Total to Date: {current_month}")

    elif choice == "👨‍🦱 Add Worker Info":
        st.subheader("Add New Worker")
        
        with st.form("add_worker_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Worker Name", key="add_name", placeholder="Enter worker name")
                join_date = st.date_input("Employee Join Date", key="add_join_date")
                gender = st.radio("Gender", options=["Male", "Female"], key="add_gender")
                phone = st.text_input("Personal Phone Number", key="add_phone", placeholder="Enter phone number")
                passport_number = st.text_input("Passport Number", key="add_passport", placeholder="Enter passport number")
                passport_expiry = st.date_input("Passport Expiry Date", key="add_passport_expiry")
                visa_expiry = st.date_input("Visa Expiry Date", key="add_visa_expiry")

            with col2:
                company_name = st.text_input("Current Working Company Name", key="add_company", placeholder="Enter company name")
                address = st.text_area("Address", key="add_address", placeholder="Enter address")
                state = st.selectbox("State", key="add_state", options=["Kuala Lumpur", "Selangor", "Penang", "Johor", "Other"])
                pic_details = st.text_area("Current Company PIC(Person-in-Charge) Details", key="add_pic")
                company_join_date = st.date_input("Current Company Join Date", key="add_company_join")
                base_salary = st.number_input("Worker Current Base Salary", key="add_salary", min_value=0.0, step=100.0)

            submitted = st.form_submit_button("Add Worker")
            if submitted:
                add_worker(name, join_date, gender, phone, passport_number, passport_expiry, visa_expiry,
                           company_name, address, state, pic_details, company_join_date, base_salary)
                st.success("Worker added successfully!")

    elif choice == "⚙️ Update Worker Info":
        st.subheader("Update Worker Information")
        workers_df = get_workers()
        if not workers_df.empty:
            worker_name = st.selectbox("Select Worker to Update", options=workers_df['name'].tolist())
            worker_id = workers_df[workers_df['name'] == worker_name]['id'].iloc[0]
            worker_data = get_worker(worker_id)

            if worker_data is not None:
                with st.form("update_worker_form",clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        name = st.text_input("Worker Name", key="update_name", value=worker_data['name'])
                        join_date = st.date_input("Employee Join Date", key="update_join_date", value=pd.to_datetime(worker_data['join_date']).date())
                        gender = st.radio("Gender", options=["Male", "Female"], key="update_gender", index=0 if worker_data['gender'] == "Male" else 1)
                        phone = st.text_input("Personal Phone Number", key="update_phone", value=worker_data['phone'])
                        passport_number = st.text_input("Passport Number", key="update_passport", value=worker_data['passport_number'])
                        passport_expiry = st.date_input("Passport Expiry Date", key="update_passport_expiry", value=pd.to_datetime(worker_data['passport_expiry']).date())
                        visa_expiry = st.date_input("Visa Expiry Date", key="update_visa_expiry", value=pd.to_datetime(worker_data['visa_expiry']).date())

                    with col2:
                        company_name = st.text_input("Current Working Company Name", key="update_company", value=worker_data['company_name'])
                        address = st.text_area("Address", key="update_address", value=worker_data['address'])
                        state = st.selectbox("State", key="update_state", options=["Kuala Lumpur", "Selangor", "Penang", "Johor", "Other"], index=["Kuala Lumpur", "Selangor", "Penang", "Johor", "Other"].index(worker_data['state']))
                        pic_details = st.text_area("Current Company PIC(Person-in-Charge) Details", key="update_pic", value=worker_data['pic_details'])
                        company_join_date = st.date_input("Current Company Join Date", key="update_company_join", value=pd.to_datetime(worker_data['company_join_date']).date())
                        base_salary = st.number_input("Worker Current Base Salary", key="update_salary", value=float(worker_data['base_salary']), min_value=0.0, step=100.0)

                    submitted = st.form_submit_button("Update Worker")
                    if submitted:
                        update_worker(worker_id, name, join_date, gender, phone, passport_number, passport_expiry, visa_expiry,
                                      company_name, address, state, pic_details, company_join_date, base_salary)
                        st.success("Worker information updated successfully!")
                        time.sleep(1)
                        st.rerun()
                        
            else:
                st.error(f"Error: Unable to retrieve worker data for ID {worker_id}.")
        else:
            st.warning("No workers found in the database. Please add a worker first.")

    elif choice == "Delete Worker":
        st.subheader("Delete Worker")
        workers_df = get_workers()
        if not workers_df.empty:
            worker_name = st.selectbox("Select Worker to Delete", options=workers_df['name'].tolist())
            worker_id = workers_df[workers_df['name'] == worker_name]['id'].iloc[0]

            st.warning(f"Are you sure you want to delete {worker_name}?")
            if st.button("Confirm Delete"):
                delete_worker(worker_id)
                st.success(f"{worker_name} has been deleted from the database.")
                st.rerun()
        else:
            st.warning("No workers found in the database. Please add a worker first.")

    elif choice == "👀 View Workers Info":
        st.subheader("Quick Workers Info")
        workers_df = get_workers()
        if not workers_df.empty:
            worker_name = st.selectbox("Select Worker to View", options=workers_df['name'].tolist())
            worker_id = workers_df[workers_df['name'] == worker_name]['id'].iloc[0]
            worker_data = get_worker(worker_id)

            if worker_data is not None:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### General Information")
                    st.markdown(f"**Name:** {worker_data['name']}")
                    st.markdown(f"**Join Date:** {worker_data['join_date']}")
                    st.markdown(f"**Gender:** {worker_data['gender']}")
                    st.markdown(f"**Phone:** {worker_data['phone']}")

                    st.markdown("### Passport Information")
                    st.markdown(f"**Passport Number:** {worker_data['passport_number']}")
                    st.markdown(f"**Passport Expiry:** {worker_data['passport_expiry']}")
                    st.markdown(f"**Visa Expiry:** {worker_data['visa_expiry']}")

                with col2:
                    st.markdown("### Work Related Info")
                    st.markdown(f"**Company Name:** {worker_data['company_name']}")
                    st.markdown(f"**Address:** {worker_data['address']}")
                    st.markdown(f"**State:** {worker_data['state']}")
                    st.markdown(f"**PIC Details:** {worker_data['pic_details']}")
                    st.markdown(f"**Company Join Date:** {worker_data['company_join_date']}")

                    st.markdown("### Salary Info")
                    st.markdown(f"**Base Salary:** RM {worker_data['base_salary']:.2f}")
            else:
                st.error(f"Error: Unable to retrieve worker data for ID {worker_id}.")
        else:
            st.warning("No workers found in the database. Please add a worker first.")

    elif choice == "💵 Transactions":
        st.subheader("Advance & Payout")
        workers_df = get_workers()
        with st.form("salary", clear_on_submit=True):
            if not workers_df.empty:
                worker_name = st.selectbox("Select Worker", options=workers_df['name'].tolist())
                worker_id = workers_df[workers_df['name'] == worker_name]['id'].iloc[0]
                
                amount = st.number_input("Amount", min_value=0.0, step=10.0)
                transaction_type = st.selectbox("Transaction Type", options=["Advance","Payout"])
                date = st.date_input("Date")

                # if st.button("Add Transaction"):
                #     add_transaction(int(worker_id), date, amount, transaction_type)
                #     st.success("Transaction added successfully!")
            else:
                st.warning("No workers found in the database. Please add a worker first.")
            submitted = st.form_submit_button("Add Transaction")
            if submitted:
                add_transaction(int(worker_id), date, amount, transaction_type)
                st.success("Transaction added successfully!")
                

    elif choice == "📊 Report":
        st.subheader("Transactions Report")
        workers_df = get_workers()
        if not workers_df.empty:
            worker_name = st.selectbox("Select Worker", options=workers_df['name'].tolist())
            worker_id = workers_df[workers_df['name'] == worker_name]['id'].iloc[0]
            
            earliest_year = get_earliest_transaction_year()
            years = range(datetime.now().year, earliest_year - 1, -1)
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            year_month = st.selectbox("Select Month", options=[f"{year}-{month}" for year in years for month in months])
            year, month = year_month.split('-')
            month_num = months.index(month) + 1

            transactions_df = get_transactions(worker_id, year, month_num)

            st.write(f"Transaction Details for {worker_name}")
            tf = transactions_df[['date','amount','transaction_type']]
            st.dataframe(tf)

            total_payout = transactions_df[transactions_df['transaction_type'] == 'Payout']['amount'].sum()
            total_advance = transactions_df[transactions_df['transaction_type'] == 'Advance']['amount'].sum()
            worker_data = get_worker(worker_id)
            base_salary = worker_data['base_salary'] if worker_data is not None else 0
            remaining = base_salary - total_payout - total_advance

            st.write(f"Base Salary: RM {base_salary:.2f}")
            st.write(f"Total Payout: RM {total_payout:.2f}")
            st.write(f"Total Advance: RM {total_advance:.2f}")
            st.write(f"Remaining: RM {remaining:.2f}")
        else:
            st.warning("No workers found in the database. Please add a worker first.")

if __name__ == '__main__':
    main()