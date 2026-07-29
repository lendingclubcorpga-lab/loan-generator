import streamlit as st
from fpdf import FPDF
import datetime
from dateutil.relativedelta import relativedelta

# --- 1. GLOBAL PAGE CONFIGURATION ---
st.set_page_config(page_title="Avant Instant Loan Portal", page_icon="💰")

st.title("💰 Instant Loan Approval Portal")
st.write("Fill out the form below to receive your instant approval decision and letter.")
st.divider()

# --- 2. CUSTOMER FORM SETUP ---
st.subheader("📝 Customer Information")
col1, col2 = st.columns(2)

with col1:
    full_name = st.text_input("Full Name", placeholder="John Doe")
    email = st.text_input("Email Address", placeholder="john@example.com")
    monthly_income = st.number_input("Monthly Gross Income ($)", min_value=1, value=5000, step=100)

with col2:
    loan_amount = st.number_input("Requested Loan Amount ($)", min_value=1, value=5000, step=500)
    loan_term = st.selectbox("Repayment Term", options=[12, 24, 36, 48, 60], index=2, format_func=lambda x: f"{x} Months")
    current_debts = st.number_input("Current Monthly Debt Payments ($)", min_value=0, value=500, step=50)

st.divider()

# --- 3. LIVE FINANCIAL CALCULATIONS ---
# These run natively on change to prevent conditional button state freezing
fixed_interest_rate = 0.08  
origination_fee_pct = 0.025  

# A. Monthly Repayment Calculation
monthly_interest_rate = fixed_interest_rate / 12
est_monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**loan_term) / ((1 + monthly_interest_rate)**loan_term - 1)

# B. Loan Breakdown Metrics
origination_fee = loan_amount * origination_fee_pct
net_disbursed_amount = loan_amount - origination_fee
total_repayment_amount = est_monthly_payment * loan_term
total_interest = total_repayment_amount - loan_amount
total_cost_of_loan = total_interest + origination_fee

# C. Regulatory TILA APR Binary Search Solver
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

# D. Underwriting Framework (DTI check)
total_future_debt = current_debts + est_monthly_payment
dti_ratio = total_future_debt / monthly_income

# --- 4. OUTPUT WORKFLOWS ---
if not full_name or not email:
    st.info("💡 Please complete the customer's name and email fields above to generate the file options.")

elif dti_ratio > 0.45:
    st.error(f"❌ Application Declined: Debt-to-Income ratio ({dti_ratio*100:.1f}%) exceeds our 45% regulatory limit.")
    st.info("💡 Recommendation: Adjust the submission parameters by reducing the principal or extending the term window.")

else:
    st.success("🎉 Underwriting Profile Clear: Application Provisionally Approved.")
    
    # Live Screen Preview Metrics Dashboard
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Est. Monthly Payment", f"${est_monthly_payment:,.2f}")
    m_col2.metric("Calculated APR", f"{calculated_apr*100:.2f}%")
    m_col3.metric("DTI Ratio", f"{dti_ratio*100:.1f}%")
    
    # --- 5. NATIVE FILE GENERATION ENGINE ---
    pdf = FPDF()
    pdf.add_page()
    
    # Avant Header Blue Band Accent
    pdf.set_fill_color(20, 35, 60)
    pdf.rect(0, 0, 210, 40, "F")
    
    # Corporate Header Letterhead Typography
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "AVANT", align="L")
    pdf.ln(15)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Personal Loans & Financial Services", align="L")
    pdf.ln(15)
    
    # Letter Context Layout Formatting
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
    
    # Table Matrix Generation Function Helper
    def add_table_row(label, val):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(90, 9, f" {label}", border=1)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(95, 9, f" {val}", border=1)
        pdf.ln(9)

    # Append financial cells into the grid sheet
    add_table_row("Requested Loan Amount (Principal):", f"${loan_amount:,.2f}")
    add_table_row("Stated Base Interest Rate:", f"{fixed_interest_rate*100:.2f}% Fixed")
    add_table_row("Annual Percentage Rate (APR):", f"{calculated_apr*100:.2f}% Dynamic")
    add_table_row("Estimated Monthly Repayment:", f"${est_monthly_payment:,.2f} / Month")
    add_table_row("Total Repayment Amount:", f"${total_repayment_amount:,.2f}")
    add_table_row("Total Cost of Credit (Fees + Interest):", f"${total_cost_of_loan:,.2f}")
    add_table_row("Final Scheduled Payoff Date:", payoff_date.strftime('%B %d, %Y'))
    pdf.ln(10)
    
    # Legal Terms & Disclosures Text
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
    
    # Signature Closings Text
    pdf.set_text_color(40, 40, 40)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 5, "Avant Underwriting Operations Group")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 5, "Electronic Verification Terminal Secure Stamp")
    pdf.ln(10)
    
    # Complete document in safe byte formatting natively
    pdf_bytes = bytes(pdf.output())
    
    # --- 6. INSTANT PERSISTENT DOWNLOAD ACTIONS ---
    st.download_button(
        label="📥 Download Official Approval PDF",
        data=pdf_bytes,
        file_name=f"Avant_Approval_{full_name.replace(' ', '_')}.pdf",
        mime="application/pdf",
        type="primary"
    )
