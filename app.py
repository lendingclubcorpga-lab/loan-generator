import streamlit as st
from fpdf import FPDF
import datetime
from dateutil.relativedelta import relativedelta

# --- 1. GLOBAL PAGE CONFIGURATION ---
# Crucial: This MUST be the first Streamlit command called and can only be called once!
st.set_page_config(page_title="Avant Instant Loan Portal", page_icon="💰")

# --- 2. TEAM LOGIN CREDENTIALS CONFIGURATION ---
TEAM_ACCOUNTS = {
    "admin": "AvantTeam2026!",
    "agent1": "SecureLoanPass1",
    "agent2": "SecureLoanPass2"
}

if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# --- 3. LOGIN SCREEN INTERFACE ---
if not st.session_state["logged_in"]:
    st.title("🔒 Team Portal Login")
    st.write("Please enter your authorized Team credentials to access the loan generator.")
    st.divider()
    
    user_id = st.text_input("User ID", placeholder="Enter your user ID")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    
    if st.button("Log In", type="primary"):
        if user_id in TEAM_ACCOUNTS and TEAM_ACCOUNTS[user_id] == password:
            st.session_state["logged_in"] = True
            st.rerun() 
        else:
            st.error("❌ Invalid User ID or Password. Please try again.")

# --- 4. PROTECTED LOAN GENERATOR INTERFACE ---
else:
    with st.sidebar:
        st.write("### 👤 Team Session")
        if st.button("🔒 Log Out"):
            st.session_state["logged_in"] = False
            st.rerun()

    st.title("💰 Instant Loan Approval Portal")
    st.write("Fill out the form below to receive your instant approval decision and letter.")
    st.divider()

    st.subheader("📝 Customer Information")
    col1, col2 = st.columns(2)

    with col1:
        full_name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email Address", placeholder="john@example.com")
        monthly_income = st.number_input("Monthly Gross Income ($)", min_value=0, value=5000, step=100)

    with col2:
        loan_amount = st.number_input("Requested Loan Amount ($)", min_value=0, value=5000, step=500)
        loan_term = st.selectbox("Repayment Term", options=[12, 24, 36, 48, 60], index=2, format_func=lambda x: f"{x} Months")
        current_debts = st.number_input("Current Monthly Debt Payments ($)", min_value=0, value=500, step=50)

    st.divider()
    
    if st.button("🚀 Process My Loan Application", type="primary"):
        if not full_name or not email:
            st.error("❌ Please fill in your name and email address to proceed.")
        elif loan_amount <= 0 or monthly_income <= 0:
            st.error("❌ Please enter valid loan and income amounts.")
        else:
            fixed_interest_rate = 0.08  
            origination_fee_pct = 0.025  
            
            # A. Calculate Base Monthly Payment
            monthly_interest_rate = fixed_interest_rate / 12
            est_monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**loan_term) / ((1 + monthly_interest_rate)**loan_term - 1)
            
            # B. Calculate Loan Fee Metrics
            origination_fee = loan_amount * origination_fee_pct
            net_disbursed_amount = loan_amount - origination_fee
            total_repayment_amount = est_monthly_payment * loan_term
            total_interest = total_repayment_amount - loan_amount
            total_cost_of_loan = total_interest + origination_fee
            
            # C. Solve for TILA Regulatory APR
            def solve_apr(net_cash, pmt, months):
                low = 0.0
                high = 1.0
                for _ in range(100):  
                    mid = (low + high) / 2
                    rate = mid / 12
                    if rate == 0:
                        calculated_pv = pmt * months
                    else:
                        calculated_pv = pmt * (1 - (1 + rate)**-months) / rate
                    
                    if calculated_pv > net_cash:
                        low = mid
                    else:
                        high = mid
                return (low + high) / 2

            calculated_apr = solve_apr(net_disbursed_amount, est_monthly_payment, loan_term)
            
            # D. Payoff Date
            today = datetime.date.today()
            payoff_date = today + relativedelta(months=loan_term)
            
            # E. Debt-to-Income Framework Check
            total_future_debt = current_debts + est_monthly_payment
            dti_ratio = total_future_debt / monthly_income

            if dti_ratio > 0.45:
                st.error(f"❌ Application Declined: Your Debt-to-Income ratio ({dti_ratio*100:.1f}%) exceeds our maximum limit.")
                st.info("💡 Try requesting a lower loan amount or extending your repayment term.")
            else:
                st.success("🎉 Congratulations! Your Avant loan has been provisionally approved.")
                
                # --- 5. GENERATE AND COMPILE PDF ---
                pdf = FPDF()
                pdf.add_page()
                
                # Draw Avant Header Blue Banner
                pdf.set_fill_color(20, 35, 60)
                pdf.rect(0, 0, 210, 40, "F")
                
                # Avant Logo
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Helvetica", "B", 24)
                pdf.cell(0, 15, "AVANT", align="L")
                pdf.ln(15)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 5, "Personal Loans & Financial Services", align="L")
                pdf.ln(15)
                
                # Document Body Formatting
                pdf.set_text_color(40, 40, 40)
                pdf.set_font("Helvetica", "B", 16)
                pdf.cell(0, 10, "APPROVAL LOAN LETTER", align="L")
                pdf.ln(10)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 5, f"Issued Date: {today.strftime('%B %d, %Y')}", align="L")
                pdf.ln(5)
                pdf.cell(0, 5, f"Offer Expiration: {(today + datetime.timedelta(days=30)).strftime('%B %d, %Y')}", align="L")
                pdf.ln(10)
                
                pdf.set_font("Helvetica", "", 11)
                intro_text = (
                    f"Dear {full_name},\n\n"
                    f"We are pleased to inform you that you have been approved for an Avant personal loan offer "
                    f"based on the initial application parameters submitted to our web terminal. Below you will find your customized "
                    f"financial breakdown details, automated APR calculations, and disclosure terms:"
                )
                pdf.multi_cell(0, 6, intro_text)
                pdf.ln(6)
                
                def add_table_row(label, val):
                    pdf.set_font("Helvetica", "B", 11)
                    pdf.cell(90, 9, f" {label}", border=1)
                    pdf.set_font("Helvetica", "", 11)
                    pdf.cell(95, 9, f" {val}", border=1)
                    pdf.ln(9)

                add_table_row("Requested Loan Amount (Principal):", f"${loan_amount:,.2f}")
                add_table_row("Stated Base Interest Rate:", f"{fixed_interest_rate*100:.2f}% Fixed")
                add_table_row("Annual Percentage Rate (APR):", f"{calculated_apr*100:.2f}% Dynamic")
                
                # --- NEW COMPILATION AND DOWNLOAD BUTTON CODE ---
                # 1. Output the PDF as a string from memory
                pdf_string = pdf.output(dest='S')
                
                # 2. Encode it into standard binary formatting
                pdf_bytes = pdf_string.encode('latin-1')
                
                # 3. Add a separation spacing element
                st.write("")
                
                # 4. Display download widget underneath successful screen metrics
                st.download_button(
                    label="📥 Download Official Approval PDF",
                    data=pdf_bytes,
                    file_name=f"Avant_Approval_{full_name.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    type="secondary"
                )
