import streamlit as st
import datetime
from fpdf import FPDF
import os
from num2words import num2words

st.set_page_config(page_title="Royal Billing", layout="centered")

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []

# ==========================
# YAHAN HAR CLIENT KA NAAM BADLO - LOCKED
# ==========================
SHOP_NAME = "Sharma Garments"
SHOP_ADDR = "Itwari, Nagpur"
SHOP_MOBILE = "98230XXXXX"
MY_NAME = "Powered by M Saad Software - 7387246146 | Dhad"
# ==========================

# --- TRIAL ---
FILE = "install_date.txt"
def get_install_date():
    if not os.path.exists(FILE):
        with open(FILE, "w") as f: f.write(str(datetime.date.today()))
        return datetime.date.today()
    try:
        with open(FILE, "r") as f: return datetime.date.fromisoformat(f.read().strip())
    except: return datetime.date.today()

install_date = get_install_date()
days_left = 7 - (datetime.date.today() - install_date).days

if days_left < 0:
    st.error("Trial Khatam")
    st.link_button("Payment Karo", "https://razorpay.me/@royalclothing")
    st.stop()
else:
    st.success(f"Trial Active Hai - {days_left} Din Bache Hai")

st.title(f"👑 {SHOP_NAME}")
st.caption(f"{SHOP_ADDR} | {SHOP_MOBILE}")
st.write("---")

# --- ADD ITEM WITH GST ---
c1,c2,c3,c4 = st.columns(4)
with c1: item_name = st.text_input("Item Name")
with c2: qty = st.number_input("Qty", 1, 100, 1)
with c3: price = st.number_input("Price", 0.0)
with c4: gst = st.number_input("GST %", 0.0, 40.0, 18.0)

if st.button("Add Item"):
    if item_name:
        st.session_state.bill_items.append({"name":item_name,"qty":qty,"price":price,"gst":gst})
        st.rerun()

# Show items
subtotal = 0
for i, it in enumerate(st.session_state.bill_items):
    amt = it['qty']*it['price']
    subtotal += amt
    st.write(f"{i+1}. {it['name']} | {it['qty']} x {it['price']} = {amt} | GST {it['gst']}%")

discount = st.number_input("Discount Rs", 0.0)
cust_name = st.text_input("Customer Name", "Customer")
cust_phone = st.text_input("Customer Phone", "")

if st.button("🧾 Bill Banao & PDF Download Karo"):
    # Calculation
    total_tax = 0
    for it in st.session_state.bill_items:
        total_tax += (it['qty']*it['price'] * it['gst']/100)

    final_total = subtotal + total_tax - discount
    cgst = total_tax/2
    sgst = total_tax/2

    pdf = FPDF()
    pdf.add_page()
    # Header
    pdf.set_fill_color(16, 37, 77)
    pdf.rect(0,0,210,28,'F')
    pdf.set_y(8)
    pdf.set_font("Arial","B",14)
    pdf.set_text_color(255,215,0)
    pdf.cell(0,8,SHOP_NAME,align="C",ln=True)
    pdf.set_font("Arial","",9)
    pdf.set_text_color(255,255,255)
    pdf.cell(0,5,f"{SHOP_ADDR} | Ph: {SHOP_MOBILE}",align="C",ln=True)
    pdf.ln(15)

    # Bill Info
    bill_no = f"INV-{datetime.date.today().strftime('%Y-%m%d')}-{len(st.session_state.bill_items)}0{st.session_state.bill_items[0]['qty'] if st.session_state.bill_items else ''}"
    pdf.set_text_color(0,0,0)
    pdf.set_font("Arial","B",8)
    pdf.cell(100,5,f"Bill No: {bill_no}")
    pdf.cell(0,5,f"Date: {datetime.date.today().strftime('%d-%m-%Y')}",align="R",ln=True)
    pdf.cell(100,5,f"Bill To: {cust_name}")
    pdf.cell(0,5,f"Phone: {cust_phone}",align="R",ln=True)
    pdf.set_font("Arial","",7)
    pdf.cell(0,5,"Supply Type: Intra-State (CGST+SGST)",ln=True)
    pdf.ln(3)

    # Table
    pdf.set_font("Arial","B",8)
    pdf.set_fill_color(16, 37, 77)
    pdf.set_text_color(255,215,0)
    pdf.cell(55,7,"Item",1,0,"C",True)
    pdf.cell(15,7,"Qty",1,0,"C",True)
    pdf.cell(30,7,"Price",1,0,"C",True)
    pdf.cell(20,7,"GST%",1,0,"C",True)
    pdf.cell(30,7,"Tax Amt",1,0,"C",True)
    pdf.cell(30,7,"Total",1,1,"C",True)

    pdf.set_font("Arial","",8)
    pdf.set_text_color(0,0,0)
    for it in st.session_state.bill_items:
        tax_amt = it['qty']*it['price']*it['gst']/100
        total_item = it['qty']*it['price']
        pdf.cell(55,7,f"{it['name']}",1,0,"C")
        pdf.cell(15,7,f"{it['qty']}",1,0,"C")
        pdf.cell(30,7,f"{it['price']:.2f}",1,0,"C")
        pdf.cell(20,7,f"{it['gst']}%",1,0,"C")
        pdf.cell(30,7,f"{tax_amt:.2f}",1,0,"C")
        pdf.cell(30,7,f"{total_item:.2f}",1,1,"C")

    # Totals
    pdf.set_font("Arial","",8)
    pdf.cell(120,6,"",0,0)
    pdf.cell(30,6,"Subtotal:",0,0,"R")
    pdf.cell(30,6,f"Rs {subtotal:.2f}",0,1,"R")
    pdf.cell(120,6,"",0,0)
    pdf.cell(30,6,"CGST:",0,0,"R")
    pdf.cell(30,6,f"Rs {cgst:.2f}",0,1,"R")
    pdf.cell(120,6,"",0,0)
    pdf.cell(30,6,"SGST:",0,0,"R")
    pdf.cell(30,6,f"Rs {sgst:.2f}",0,1,"R")
    pdf.set_font("Arial","B",8)
    pdf.set_text_color(180,70,0)
    pdf.cell(120,6,"",0,0)
    pdf.cell(30,6,"Total GST:",0,0,"R")
    pdf.cell(30,6,f"Rs {total_tax:.2f}",0,1,"R")
    pdf.set_text_color(0,150,0)
    pdf.cell(120,6,"",0,0)
    pdf.cell(30,6,"Discount:",0,0,"R")
    pdf.cell(30,6,f"- Rs {discount:.2f}",0,1,"R")
    pdf.ln(2)
    pdf.set_fill_color(16, 37, 77)
    pdf.set_text_color(255,215,0)
    pdf.cell(120,8,"FINAL PAYABLE:",1,0,"R",True)
    pdf.cell(60,8,f"Rs {final_total:.2f}",1,1,"C",True)

    pdf.ln(4)
    pdf.set_text_color(0,0,0)
    pdf.set_font("Arial","B",7)
    try:
        words = num2words(final_total, to='currency', lang='en_IN').replace(',','')
        pdf.cell(0,5,f"In Words: {words} Only",ln=True)
    except:
        pdf.cell(0,5,f"In Words: {final_total} Rupees Only",ln=True)

    pdf.ln(10)
    pdf.set_font("Arial","",8)
    pdf.cell(0,5,"For Shop",align="R",ln=True)
    pdf.ln(6)
    pdf.set_font("Arial","B",8)
    pdf.cell(0,5,"Authorised Signature",align="R",ln=True)
    pdf.ln(10)
    pdf.set_font("Arial","I",7)
    pdf.set_text_color(100,100,100)
    pdf.cell(0,5,MY_NAME + " | Thank you visit again!",align="C",ln=True)

    pdf.output("bill.pdf")
    with open("bill.pdf","rb") as f:
        st.download_button("📥 Download PDF", f, file_name=f"{cust_name}_Bill.pdf")

if st.button("Clear Bill"):
    st.session_state.bill_items = []
    st.rerun()