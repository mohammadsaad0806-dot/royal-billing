import streamlit as st
from fpdf import FPDF
from datetime import datetime, date, timedelta
import os, hashlib

st.set_page_config(page_title="M Saad Royal Billing", layout="centered")

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []

# ============================================================
# CLIENT LOCK - HAR CLIENT KE LIYE YAHAN NAAM BADLO
# ============================================================
SELLER_NAME = "Sharma Garments"
SELLER_ADDRESS = "Itwari, Nagpur"
SELLER_PHONE = "98230XXXXX"
SELLER_EMAIL = "sharma@gmail.com"
SELLER_GSTIN = ""
MY_FOOTER = "Powered by M Saad Software - 7387246146"
# ============================================================

# Secret - Isi se secure key banegi, isko change mat karna
SECRET = "Saad@1999_Billing"

# --- WORDS LOGIC ---
ONES = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen", "Nineteen"]
TENS = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
def number_to_words(n):
    n=int(n)
    if n==0: return "Zero"
    if n<20: return ONES[n]
    if n<100: return TENS[n//10] + (" " + ONES[n%10] if n%10 else "")
    if n<1000: return ONES[n//100] + " Hundred" + (" " + number_to_words(n%100) if n%100 else "")
    if n<100000: return number_to_words(n//1000) + " Thousand" + (" " + number_to_words(n%1000) if n%1000 else "")
    if n<10000000: return number_to_words(n//100000) + " Lakh" + (" " + number_to_words(n%100000) if n%100000 else "")
    return number_to_words(n//10000000) + " Crore" + (" " + number_to_words(n%10000000) if n%10000000 else "")
def amount_in_words(amount):
    rupees=int(amount); paise=int(round((amount-rupees)*100))
    result=number_to_words(rupees)+" Rupees"
    if paise>0: result+=" and "+number_to_words(paise)+" Paise"
    return result+" Only"
def get_next_invoice_number():
    os.makedirs("M_Saad_Bills", exist_ok=True)
    file="M_Saad_Bills/invoice_counter.txt"
    try: num=int(open(file).read()) if os.path.exists(file) else 0
    except: num=0
    num+=1; open(file,"w").write(str(num))
    return f"INV-{datetime.now().year}-{num:05d}"

# ============================================================
# SECURE MONTHLY SYSTEM - AB GUESS NAHI HOGA
# ============================================================
LICENSE_FILE = "license.txt"
INSTALL_FILE = "install_date.txt"

def get_install_date():
    if not os.path.exists(INSTALL_FILE):
        open(INSTALL_FILE,"w").write(str(date.today())); return date.today()
    try: return date.fromisoformat(open(INSTALL_FILE).read().strip())
    except: return date.today()

install_date = get_install_date()
trial_days_left = 7 - (date.today() - install_date).days

def generate_hash(shop, days):
    raw = f"{shop.upper()}{days}{SECRET}"
    return hashlib.sha256(raw.encode()).hexdigest()[:6].upper()

def check_license():
    if os.path.exists(LICENSE_FILE):
        try:
            expiry = date.fromisoformat(open(LICENSE_FILE).read().strip())
            if expiry >= date.today(): return True, (expiry - date.today()).days
        except: pass
    if trial_days_left >= 0: return True, trial_days_left
    return False, 0

def activate_license(key):
    try:
        parts = key.strip().upper().split("-")
        if len(parts)!=4 or parts[0]!="MSAAD": return False
        shop_code = parts[1]
        days = int(parts[2])
        hash_code = parts[3]
        real_hash = generate_hash(shop_code, days)
        if hash_code == real_hash:
            expiry = date.today() + timedelta(days=days)
            open(LICENSE_FILE,"w").write(str(expiry))
            return True
        return False
    except: return False

is_active, days_remaining = check_license()

st.sidebar.title("🔑 License Panel")
if is_active:
    if os.path.exists(LICENSE_FILE): st.sidebar.success(f"Licensed: {days_remaining} Din")
    else: st.sidebar.success(f"Trial: {days_remaining} Din Bache")
else: st.sidebar.error("License Khatam")
st.sidebar.write("---")
key_input = st.sidebar.text_input("License Key")
if st.sidebar.button("Activate Karo"):
    if activate_license(key_input):
        st.sidebar.success("Activated!")
        st.rerun()
    else: st.sidebar.error("Galat Key!")

if not is_active:
    st.error("⏰ Trial / License Khatam Ho Gaya")
    st.markdown(f"### {SELLER_NAME} - Subscription Lo\n**Monthly: 199 | Yearly: 1499**\nGPay: 7387246146")
    st.link_button("💳 Payment Karo", "https://razorpay.me/@royalclothing")
    st.stop()

# ============================================================
# BILLING APP
# ============================================================
st.title(f"👑 {SELLER_NAME}")
st.caption(f"{SELLER_ADDRESS} | {SELLER_PHONE}")
st.subheader("Customer Details")
c1,c2=st.columns(2)
with c1: cust_name=st.text_input("Customer Name", "Abutalha")
with c2: cust_phone=st.text_input("Phone", "1273275821")
cust_addr=st.text_input("Address", "AP road")
supply=st.radio("Supply Type", ["Intra-State (CGST+SGST)", "Inter-State (IGST)"], horizontal=True)
supply_type="intra" if "Intra" in supply else "inter"
st.write("---")
st.subheader("Add Item")
ic1,ic2,ic3,ic4=st.columns(4)
with ic1: iname=st.text_input("Item Name")
with ic2: iqty=st.number_input("Qty",1,1000,1)
with ic3: iprice=st.number_input("Price",0.0)
with ic4: igst=st.selectbox("GST%",[0,5,12,18,28], index=2)
if st.button("Add Item"):
    if iname:
        st.session_state.bill_items.append({"item":iname,"qty":iqty,"price":iprice,"gst":igst})
        st.rerun()
discount=st.number_input("Discount Rs",0.0)
if st.session_state.bill_items:
    for idx, it in enumerate(st.session_state.bill_items):
        st.write(f"{idx+1}. {it['item']} - {it['qty']} x {it['price']} - GST {it['gst']}%")

if st.button("🧾 Royal PDF Banao"):
    if not st.session_state.bill_items: st.warning("Pehle item add karo"); st.stop()
    bill_no=get_next_invoice_number()
    class InvoicePDF(FPDF):
        def header(self):
            self.set_fill_color(15,32,64); self.rect(0,0,210,34,"F"); self.set_y(6)
            self.set_font("helvetica","B",18); self.set_text_color(255,215,0); self.cell(0,9,SELLER_NAME,align="C",ln=True)
            self.set_font("helvetica","",8); self.set_text_color(255,255,255); self.cell(0,5,SELLER_ADDRESS,align="C",ln=True)
            self.cell(0,5,f"Phone: {SELLER_PHONE} | Email: {SELLER_EMAIL}",align="C",ln=True)
        def footer(self):
            self.set_y(-18); self.set_font("helvetica","",8); self.set_text_color(100,100,100); self.cell(0,5,f"Thank you! | {MY_FOOTER}",align="C",ln=True)
    pdf=InvoicePDF(); pdf.set_auto_page_break(auto=True, margin=20); pdf.add_page(); pdf.set_y(40)
    pdf.set_font("helvetica","B",10); pdf.set_text_color(15,32,64); pdf.cell(100,7,f"Invoice No: {bill_no}")
    pdf.set_font("helvetica","",10); pdf.set_text_color(80,80,80); pdf.cell(0,7,f"Date: {datetime.now().strftime('%d-%m-%Y')}",align="R",ln=True)
    pdf.ln(4); pdf.set_fill_color(240,245,255); pdf.set_draw_color(180,190,210); y=pdf.get_y(); pdf.rect(10,y,190,22,"DF")
    pdf.set_xy(14,y+3); pdf.set_font("helvetica","B",11); pdf.set_text_color(0,90,170); pdf.cell(0,6,f"BILL TO: {cust_name}",ln=True)
    pdf.set_font("helvetica","",9); pdf.set_text_color(60,60,60); pdf.set_x(14); pdf.cell(0,5,f"Phone: {cust_phone} | Address: {cust_addr}",ln=True)
    pdf.set_y(y+26); pdf.set_font("helvetica","B",10); pdf.set_text_color(15,32,64)
    pdf.cell(0,7,"Supply Type: Intra-State (CGST + SGST)" if supply_type=="intra" else "Supply Type: Inter-State (IGST)",ln=True); pdf.ln(2)
    col_widths=[48,18,28,22,24,45]; headers=["Item","Qty","Price","GST %","Tax","Amount"]
    pdf.set_fill_color(15,32,64); pdf.set_text_color(255,215,0); pdf.set_font("helvetica","B",9)
    for i,h in enumerate(headers): pdf.cell(col_widths[i],9,h,border=1,align="C",fill=True)
    pdf.ln(); subtotal=0.0; total_gst=0.0
    for idx,data in enumerate(st.session_state.bill_items):
        base=data["qty"]*data["price"]; tax=base*(data["gst"]/100.0); subtotal+=base; total_gst+=tax
        pdf.set_fill_color(240,245,255) if idx%2==0 else pdf.set_fill_color(255,255,255)
        pdf.set_font("helvetica","",9); pdf.set_text_color(20,20,20)
        pdf.cell(col_widths[0],8,data["item"][:28],border=1,align="C",fill=True); pdf.cell(col_widths[1],8,str(data["qty"]),border=1,align="C",fill=True)
        pdf.cell(col_widths[2],8,f"{data['price']:.2f}",border=1,align="C",fill=True); pdf.cell(col_widths[3],8,f"{data['gst']:g}%",border=1,align="C",fill=True)
        pdf.cell(col_widths[4],8,f"{tax:.2f}",border=1,align="C",fill=True); pdf.cell(col_widths[5],8,f"{base+tax:.2f}",border=1,align="C",fill=True); pdf.ln()
    taxable_value=subtotal-discount;
    if taxable_value<0: taxable_value=0
    discount_ratio=taxable_value/subtotal if subtotal>0 else 0; adjusted_gst=total_gst*discount_ratio if subtotal>0 else 0; final_bill=taxable_value+adjusted_gst
    cgst=adjusted_gst/2 if supply_type=="intra" else 0; sgst=adjusted_gst/2 if supply_type=="intra" else 0; igst=adjusted_gst if supply_type=="inter" else 0
    pdf.ln(5); pdf.set_font("helvetica","",10); pdf.set_text_color(60,60,60)
    pdf.cell(135,7,"Subtotal:",align="R"); pdf.cell(0,7,f"Rs {subtotal:.2f}",align="R",ln=True)
    if discount>0: pdf.set_text_color(180,60,20); pdf.cell(135,7,"Discount:",align="R"); pdf.cell(0,7,f"- Rs {discount:.2f}",align="R",ln=True)
    pdf.set_text_color(60,60,60); pdf.cell(135,7,"Taxable Value:",align="R"); pdf.cell(0,7,f"Rs {taxable_value:.2f}",align="R",ln=True)
    if supply_type=="intra":
        pdf.cell(135,7,"CGST:",align="R"); pdf.cell(0,7,f"Rs {cgst:.2f}",align="R",ln=True); pdf.cell(135,7,"SGST:",align="R"); pdf.cell(0,7,f"Rs {sgst:.2f}",align="R",ln=True)
    else: pdf.cell(135,7,"IGST:",align="R"); pdf.cell(0,7,f"Rs {igst:.2f}",align="R",ln=True)
    pdf.set_text_color(200,80,0); pdf.set_font("helvetica","B",10); pdf.cell(135,7,"Total GST:",align="R"); pdf.cell(0,7,f"Rs {adjusted_gst:.2f}",align="R",ln=True)
    pdf.ln(3); pdf.set_fill_color(15,32,64); pdf.set_text_color(255,215,0); pdf.set_font("helvetica","B",13)
    pdf.cell(135,12,"FINAL PAYABLE:",align="R",fill=True); pdf.cell(0,12,f"Rs {final_bill:.2f}",align="R",fill=True,ln=True)
    pdf.ln(4); pdf.set_font("helvetica","B",9); pdf.set_text_color(15,32,64); pdf.cell(0,6,"Amount in Words:",ln=True)
    pdf.set_font("helvetica","",9); pdf.set_text_color(60,60,60); pdf.multi_cell(0,5,amount_in_words(final_bill))
    pdf.output("bill.pdf")
    with open("bill.pdf","rb") as f: st.download_button("📥 Download Royal Bill", f, file_name=f"{cust_name}_{bill_no}.pdf")

if st.button("Clear All"): st.session_state.bill_items=[]; st.rerun()