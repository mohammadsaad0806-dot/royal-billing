import streamlit as st
import datetime
from fpdf import FPDF
import json, os

st.set_page_config(page_title="Royal Billing", layout="centered")

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []

# --- SUBSCRIPTION LOGIC ---
TRIAL_DAYS = 7
FILE = "install_date.txt"

def get_install_date():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f:
            f.write(str(datetime.date.today()))
        return datetime.date.today()
    else:
        with open(FILE, "r") as f:
            return datetime.date.fromisoformat(f.read().strip())

install_date = get_install_date()
today = datetime.date.today()
days_used = (today - install_date).days
days_left = TRIAL_DAYS - days_used

if days_left < 0:
    st.error("⏰ Aapka 7 Din ka Free Trial Khatam Ho Gaya Hai")
    st.markdown("""
    ### Royal Billing Pro - Subscription Le
    **Monthly: Rs 199** | **Yearly: Rs 1999 (2 mahine free)**
    
    Payment ke liye neeche click karo:
    """)
    st.link_button("💳 Abhi Payment Karo (Razorpay/UPI)", "https://razorpay.me/@royalclothing")
    st.info("Payment ke baad screenshot WhatsApp karo: 8000000000 par. Hum 5 min me activate kar denge.")
    st.stop()
else:
    st.success(f"✅ Trial Active Hai - {days_left} Din Bache Hai")

# --- BILLING APP ---
st.title("👑 Royal Clothing - Billing")
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
    st.write(f"{i+1}. {it['name']} - {it['qty']} x {it['price']} = Rs {amt}")

st.write("---")
st.subheader(f"Total: Rs {total}")
cust_name = st.text_input("Customer Name", "Customer")

if st.button("🧾 Bill Banao & PDF Download Karo"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, "Royal Clothing - Nagpur", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.set_font("Arial", "", 12)
    pdf.cell(200, 10, f"Customer: {cust_name} | Date: {today}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(200, 10, f"Total: Rs {total}", new_x="LMARGIN", new_y="NEXT")
    for it in st.session_state.bill_items:
        pdf.cell(200, 8, f"{it['name']} - {it['qty']} x {it['price']} = {it['qty']*it['price']}", new_x="LMARGIN", new_y="NEXT")
    pdf.output("bill.pdf")
    with open("bill.pdf", "rb") as f:
        st.download_button("📥 Download Bill PDF", f, file_name=f"bill_{cust_name}.pdf")

if st.button("Clear Bill"):
    st.session_state.bill_items = []
    st.rerun()
