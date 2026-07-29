import streamlit as st
from fpdf import FPDF
import datetime
from dateutil.relativedelta import relativedelta

# --- 1. GLOBAL PAGE CONFIGURATION ---
st.set_page_config(page_title="Avant Instant Loan Portal", page_icon="💰")

# --- 2. TEAM LOGIN CREDENTIALS CONFIGURATION ---
TEAM_ACCOUNTS = {
    "admin": "AvantTeam2026!",
    "agent1": "SecureLoanPass1",
    "agent2": "SecureLoanPass2"
}

# Initialize session state flags safely
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "app_processed" not in st.session_state:
    st.session_state["app_processed"] = False
if "pdf_bytes" not in st.session_state:
    st.session_state["pdf_bytes"] = None
if "pdf_filename" not in st.session_state:
    st.session_state["pdf_filename"] = ""

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
        
        # Reset current customer application session helper
        if st.session_state["app_processed"]:
            if st.button("🔄 Clear & New Application", type="secondary"):
                st.session_state["app_processed"] = False
                st.session_state["pdf_bytes"] = None
                st.session_state["pdf_filename"] = ""
                st.rerun()
                
        if st.button("🔒 Log Out", type="primary"):
            st.session_state["logged_in"] = False
            st.session_state["app_processed"] = False
            st.session_state["pdf_bytes"] = None
            st.session_state["pdf_filename"] = ""
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
        # FIXED: Numbers are now perfectly populated inside the options array list!
        loan_term = st.selectbox("Repayment Term", options=[12, 24, 36, 48, 60], index=2, format_func=lambda x: f"{x} Months")
        current_debts = st.number_input("Current Monthly Debt Payments ($)", min_value=0, value=500, step=50)

    st.divider()
    
    # Process Application Button
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
            
            # C. TILA Regulatory APR Calculation Loop
            def solve_apr(net_cash, pmt, months):
                low, high = 0.0, 1.0
                for _ in range(100):  
                    mid = (low + high) / 2
                    rate = mid / 12
                    calculated_pv = pmt * months if rate == 0 else pmt * (1 - (1 + rate)**-months) / rate
                    if calculated_pv > net_cash:
                        low = mid
                    else:
                        high = mid
                return (low + high) / 2

            calculated_apr = solve_apr(net_disbursed_amount, est_monthly_payment, loan_term)
            today = datetime.date.today()
            payoff_date = today + relativedelta(months=loan_term)
            
            # D. Debt-to-Income Framework Check
            total_future_debt = current_debts + est_monthly_payment
            dti_ratio = total_future_debt / monthly_income

            if dti_ratio > 0.45:
                st.error(f"❌ Application Declined: Your Debt-to-Income ratio ({dti_ratio*100:.1f}%) exceeds our maximum limit.")
                st.info("💡 Try requesting a lower loan amount or extending your repayment term.")
                st.session_state["app_processed"] = False
            else:
                # --- PDF COMPILATION GENERATOR ---
                pdf = FPDF()
                pdf.add_page()
                
                pdf.set_fill_color(20, 35, 60)
                pdf.rect(0, 0, 210, 40, "F")
                
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Helvetica", "B", 24)
                pdf.cell(0, 15, "AVANT", align="L")
                pdf.ln(15)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 5, "Personal Loans & Financial Services", align="L")
                pdf.ln(15)
                
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
                add_table_row("Estimated Monthly Repayment:", f"${est_monthly_payment:,.2f} / Month")
                add_table_row("Total Repayment Amount:", f"${total_repayment_amount:,.2f}")
                add_table_row("Total Cost of Credit (Fees + Interest):", f"${total_cost_of_loan:,.2f}")
                add_table_row("Final Scheduled Payoff Date:", payoff_date.strftime('%B %d, %Y'))
                pdf.ln(10)
                
                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, "Important Account Terms & Disclosures")
                pdf.ln(8)
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(100, 100, 100)
                
                disclosure_text = (
                    "This approval offer is contingent on verification of the stated monthly gross income metrics, "
                    "credit file validation, and strict underwriting checks upon completion of full signing profiles. "
                    "The APR calculations disclosed above conform to Truth-In-Lending Act (TILA) regulatory definitions. "
                    "Funds are dispatched via ACH network transfer within 1 business day of final approval validation."
                )
                pdf.multi_cell(0, 5, disclosure_text)
                pdf.ln(15)
                
                pdf.set_text_color(40, 40, 40)
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 5, "Avant Underwriting Operations Group")
                pdf.ln(5)
                pdf.set_font("Helvetica", "", 10)
                pdf.cell(0, 5, "Electronic Verification Terminal Secure Stamp")
                pdf.ln(5)
                
                # Save binary content to file state metrics safely
                st.session_state["pdf_bytes"] = bytes(pdf.output())
                st.session_state["pdf_filename"] = f"Avant_Approval_{full_name.replace(' ', '_')}.pdf"
                st.session_state["app_processed"] = True
                st.rerun()

    # --- 5. PERSISTENT REGISTRATION VIEW ---
