import streamlit as st
from fpdf import FPDF
import datetime
from dateutil.relativedelta import relativedelta

# 1. Page Title and Header Setup
st.set_page_config(page_title="Avant Instant Loan Portal", page_icon="💰")
st.title("💰 Instant Loan Approval Portal")
st.write("Fill out the form below to receive your instant approval decision and letter.")

st.divider()

# 2. Build the Customer Form Setup
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

# 3. Dynamic Underwriting and Financial Calculations
st.divider()
if st.button("🚀 Process My Loan Application", type="primary"):
    if not full_name or not email:
        st.error("❌ Please fill in your name and email address to proceed.")
    elif loan_amount <= 0 or monthly_income <= 0:
        st.error("❌ Please enter valid loan and income amounts.")
    else:
        # Define constants
        fixed_interest_rate = 0.08  # 8% Fixed Base Interest Rate
        origination_fee_pct = 0.025  # 2.5% Origination Fee
        
        # A. Calculate Base Monthly Payment using standard amortization
        monthly_interest_rate = fixed_interest_rate / 12
        est_monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate)**loan_term) / ((1 + monthly_interest_rate)**loan_term - 1)
        
        # B. Calculate Loan Fee Metrics
        origination_fee = loan_amount * origination_fee_pct
        net_disbursed_amount = loan_amount - origination_fee
        total_repayment_amount = est_monthly_payment * loan_term
        total_interest = total_repayment_amount - loan_amount
        total_cost_of_loan = total_interest + origination_fee
        
        # C. Dynamically Solve for Truth-in-Lending Act (TILA) Regulatory APR
        def solve_apr(net_cash, pmt, months):
            low = 0.0
            high = 1.0
            for _ in range(100):  # Binary search to find exact rate
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
        
        # D. Calculate Dynamic Payoff Date
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
            
            # 4. Generate the Fixed PDF Letter
            pdf = FPDF()
            pdf.add_page()
            
            # Draw Avant Style Header Brand Accent (Dark Blue Banner)
            pdf.set_fill_color(20, 35, 60)
            pdf.rect(0, 0, 210, 40, "F")
            
            # Text Avant Logo over the colored banner
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 24)
            pdf.cell(0, 15, "AVANT", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 5, "Personal Loans & Financial Services", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(15)
            
            # Reset font text color to dark grey for document body
            pdf.set_text_color(40, 40, 40)
            
            # Document Metadata Header
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "PRE-APPROVAL LOAN LETTER", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            pdf.cell(0, 5, f"Issued Date: {today.strftime('%B %d, %Y')}", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 5, f"Offer Expiration: {(today + datetime.timedelta(days=30)).strftime('%B %d, %Y')}", align="L", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            # Content Block Paragraph
            pdf.set_font("Helvetica", "", 11)
            intro_text = (
                f"Dear {full_name},\n\n"
                f"We are pleased to inform you that you have been pre-approved for an Avant personal loan offer "
                f"based on the initial application parameters submitted to our web terminal. Below you will find your customized "
                f"financial breakdown details, automated APR calculations, and disclosure terms:"
            )
            pdf.multi_cell(0, 6, intro_text)
            pdf.ln(6)
            
            # Terms Grid Table Layout
            def add_table_row(label, val):
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(90, 9, f" {label}", border=1)
                pdf.set_font("Helvetica", "", 11)
                pdf.cell(95, 9, f" {val}", border=1, new_x="LMARGIN", new_y="NEXT")

            add_table_row("Requested Loan Amount (Principal):", f"${loan_amount:,.2f}")
            add_table_row("Stated Base Interest Rate:", f"{fixed_interest_rate*100:.2f}% Fixed")
            add_table_row("Annual Percentage Rate (APR):", f"{calculated_apr*100:.2f}% Dynamic")
            add_table_row("Origination Fee (2.5%):", f"${origination_fee:,.2f}")
            add_table_row("Monthly Payment Amount:", f"${est_monthly_payment:,.2f}")
            add_table_row("Total Interest:", f"${total_interest:,.2f}")
            add_table_row("Total Cost of Loan (Interest + Fees):", f"${total_cost_of_loan:,.2f}")
            add_table_row("Total Repayment Amount:", f"${total_repayment_amount:,.2f}")
            add_table_row("Payoff Date:", payoff_date.strftime("%B %d, %Y"))
            
            pdf.ln(12)
            
            # Legal Boilerplate Terms & Conditions Layout
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(0, 5, "Mandatory Regulatory Disclosures:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "I", 9)
            terms_text = (
                "1. This pre-approval represents a conditional evaluation and does not constitute an explicit binding agreement or contract.\n"
                "2. Final funding remains conditional upon complete verification of identity, credit history validation, and income documentation.\n"
                "3. Origination fees are deducted directly from loan proceeds at funding and are incorporated into your total cost schedule.\n"
                "4. APR formulas are derived using strict financial internal rate of return metrics based on actual net disbursed loan balances."
            )
            pdf.multi_cell(0, 5, terms_text)
            
            # Output PDF directly to bytes array
            pdf_bytes = pdf.output()
            
            # 5. Display download link directly on screen
            st.download_button(
                label="📥 Download Your Avant Approval Letter (PDF)",
                data=bytes(pdf_bytes),
                file_name=f"Avant_Approval_{full_name.replace(' ', '_')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
