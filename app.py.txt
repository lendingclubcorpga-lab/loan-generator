import streamlit as st
from fpdf import FPDF
import datetime

# 1. Page Title and Header
st.set_page_config(page_title="Instant Loan Approvals", page_icon="💰")
st.title("💰 Instant Loan Approval Portal")
st.write("Fill out the form below to receive your instant approval decision and letter.")

st.divider()

# 2. Build the Customer Form
st.subheader("📝 Customer Information")
col1, col2 = st.columns(2)

with col1:
    full_name = st.text_input("Full Name", placeholder="John Doe")
    email = st.text_input("Email Address", placeholder="john@example.com")
    monthly_income = st.number_input("Monthly Gross Income ($)", min_value=0, value=5000, step=100)

with col2:
    loan_amount = st.number_input("Requested Loan Amount ($)", min_value=0, value=10000, step=500)
    loan_term = st.selectbox("Repayment Term", options=[12, 24, 36, 48, 60], format_func=lambda x: f"{x} Months")
    current_debts = st.number_input("Current Monthly Debt Payments ($)", min_value=0, value=500, step=50)

# 3. Simple Approval Underwriting Logic
st.divider()
if st.button("🚀 Process My Loan Application", type="primary"):
    if not full_name or not email:
        st.error("❌ Please fill in your name and email address to proceed.")
    else:
        # Calculate Debt-to-Income (DTI) ratio
        # Rule: Loan payment shouldn't push total monthly debt obligations over 45% of income
        estimated_interest_rate = 0.08  # 8% fixed rate proxy
        monthly_interest = estimated_interest_rate / 12
        
        # Standard amortization formula
        payment_numerator = loan_amount * monthly_interest * ((1 + monthly_interest) ** loan_term)
        payment_denominator = ((1 + monthly_interest) ** loan_term) - 1
        est_monthly_payment = payment_numerator / payment_denominator
        
        total_future_debt = current_debts + est_monthly_payment
        dti_ratio = total_future_debt / monthly_income if monthly_income > 0 else 1

        # Check approval conditions
        if dti_ratio > 0.45:
            st.error("❌ Application Declined: Your Debt-to-Income ratio exceeds our maximum limit.")
            st.info("💡 Try requesting a lower loan amount or extending your repayment term.")
        else:
            st.success("🎉 Congratulations! Your loan has been provisionally approved.")
            
            # 4. Generate the PDF Letter
            pdf = FPDF()
            pdf.add_page()
            
            # Header Layout
            pdf.set_font("Helvetica", "B", 18)
            pdf.cell(0, 10, "PRE-APPROVAL LOAN LETTER", ln=True, align="C")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 10, f"Issued Date: {datetime.date.today().strftime('%B %d, %Y')}", ln=True, align="C")
            pdf.ln(10)
            
            # Content Block
            pdf.set_font("Helvetica", "", 12)
            pdf.multi_cell(0, 8, f"Dear {full_name},\n\nWe are pleased to inform you that you have been pre-approved for a personal loan based on the preliminary information provided. Below are the details regarding your approved loan terms:")
            pdf.ln(5)
            
            # Terms Grid Table
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(70, 10, "Approved Loan Amount:", border=1)
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(110, 10, f" ${loan_amount:,.2f}", border=1, ln=True)
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(70, 10, "Repayment Term:", border=1)
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(110, 10, f" {loan_term} Months", border=1, ln=True)
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(70, 10, "Estimated Monthly Payment:", border=1)
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(110, 10, f" ${est_monthly_payment:,.2f}", border=1, ln=True)
            
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(70, 10, "Estimated Interest Rate (APR):", border=1)
            pdf.set_font("Helvetica", "", 12)
            pdf.cell(110, 10, f" {estimated_interest_rate*100:.1f}% Fixed", border=1, ln=True)
            pdf.ln(10)
            
            # Legal Boilerplate Terms & Conditions
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 5, "Terms & Conditions:", ln=True)
            pdf.set_font("Helvetica", "I", 9)
            terms_text = (
                "1. This document constitutes a conditional pre-approval only and does not represent a formal offer of credit.\n"
                "2. Final funding is strictly subject to identity verification, credit report evaluation, and income documentation.\n"
                "3. The applicant certifies that all information entered into the web portal is true and accurate.\n"
                "4. Rates and terms are subject to change based on market conditions prior to official closing."
            )
            pdf.multi_cell(0, 5, terms_text)
            
            # Output PDF to bytes
            pdf_bytes = pdf.output()
            
            # 5. Display download link directly on screen
            st.download_button(
                label="📥 Download Your Approval Letter (PDF)",
                data=bytes(pdf_bytes),
                file_name=f"Loan_Approval_{full_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
