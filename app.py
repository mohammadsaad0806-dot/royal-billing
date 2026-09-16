import streamlit as st
import datetime
from fpdf import FPDF
import os

st.set_page_config(page_title="Royal Billing", layout="centered")

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []

# ==========================
# YAHAN HAR CLIENT KA NAAM BADLO
# ==========================
SHOP_NAME = "Sharma Garments"  # yahan naam badlo
SHOP_ADDR = "Itwari, Nagpur"   # yahan address badlo
SHOP_MOBILE = "98230XXXXX"      # yahan mobile badlo
# ==========================

# --- SUBSCRIPTION LOGIC ---
TRIAL_DAYS = 7
FILE = "install_date.txt"

def get_install_date():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            f.write(str(datetime.date.today()))
        return datetime.date.today()
    else:
        try:
            with open(FILE, "r") as f:
                return datetime.date.fromisoformat(f.read().strip())
        except:
            return datetime.date.today()

install_date = get_install_date()
today = datetime.date.today()
days_used = (today - install_date).days
days_left = TRIAL_DAYS - days_used

if days_left < 0:
    st.error("⏰ Aapka 7 Din ka Free Trial Khatam Ho Gaya Hai")
    st.markdown("### Billing Pro - Subscription Le\n**Monthly: Rs 199 | Yearly: Rs 1999**")
    st.link_button("💳 Abhi Payment Karo", "https://razorpay.me/@royalclothing")
    st.info("Payment ke baad WhatsApp karo: 8000000000 par")
    st.stop()
else:
    st.success(f"✅ Trial Active Hai - {days_left} Din Bache Hai")

# --- APP UI ---
st.title(f"👑 {SHOP_NAME}")
st.caption(f"{SHOP_ADDR} | {SHOP_MOBILE}")
st.write("---")

c1, c2, c3 = st.columns(3)
with c1: item_name = st.text_input("Item Name")
with c2: qty = st.number_input("Qty", 1, 100, 1)
with c3: price = st.number_input("Price", 0)

if st.button("Add Item"):
    if item_name:
        st.session_state.bill_items.append({"name": item_name, "qty": qty, "price": price})
        st.rerun()

total = 0
for i, it in enumerate(st.session_state.bill_items):
    amt = it['qty'] * it['price']
    total += amt
    col1, col2 = st.columns([4,1])
    col1.write(f"{i+1}. {it['name']} - {it['qty']} x {it['price']}")
    col2.write(f"Rs {amt}")

st.write("---")
st.subheader(f"Total: Rs {total}")
cust_name = st.text_input("Customer Name", "Customer")

if st.button("🧾 Bill Banao & PDF Download Karo"):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, SHOP_NAME, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"{SHOP_ADDR} | Mob: {SHOP_MOBILE}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
    pdf.ln(8)
    
    # Customer Details
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Customer: {cust_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Date: {today} | Bill No: {today.strftime('%d%m%Y')}{len(st.session_state.bill_items)}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Table Header
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(240,240,240)
    pdf.cell(90, 10, " Item", border=1, fill=True)
    pdf.cell(30, 10, " Qty", border=1, align="C", fill=True)
    pdf.cell(35, 10, " Price", border=1, align="C", fill=True)
    pdf.cell(35, 10, " Amount", border=1, align="C", fill=True)
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", "", 11)
    for it in st.session_state.bill_items:
        amt = it['qty'] * it['price']
        pdf.cell(90, 9, f" {it['name']}", border=1)
        pdf.cell(30, 9, f"{it['qty']}", border=1, align="C")
        pdf.cell(35, 9, f"{it['price']}", border=1, align="C")
        pdf.cell(35, 9, f"{amt}", border=1, align="C")
        pdf.ln()
    
    # Total
    pdf.set_font("Arial", "B", 13)
    pdf.cell(155, 11, " TOTAL", border=1, align="R")
    pdf.cell(35, 11, f"Rs {total}", border=1, align="C")
    pdf.ln(15)

    # Footer - TERA NAAM
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 8, "Thank You! Visit Again", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "B", 9)
    pdf.cell(0, 6, "Powered by Mohammad Saad | Support: 8000000000", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.output("bill.pdf")
    with open("bill.pdf", "rb") as f:
        st.download_button("📥 Download Bill PDF", f, file_name=f"{SHOP_NAME}_{cust_name}.pdf")

if st.button("Clear Bill"):
    st.session_state.bill_items = []
    st.rerun()