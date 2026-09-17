import streamlit as st
from fpdf import FPDF
from datetime import datetime, date, timedelta
import os
import hashlib
import hmac

st.set_page_config(
    page_title="M Saad Royal Billing",
    layout="centered"
)

# ============================================================
# BILL ITEMS
# ============================================================

if "bill_items" not in st.session_state:
    st.session_state.bill_items = []


# ============================================================
# CLIENT DETAILS
# ============================================================

SELLER_NAME = "Mohammad Saad"
SELLER_ADDRESS = "Dhad, Buldhana"
SELLER_PHONE = "73872XXXXX"
SELLER_EMAIL = "msaad@gmail.com"
SELLER_GSTIN = ""

MY_FOOTER = "Powered by M Saad Software - 7387246146"


# ============================================================
# CUSTOMER UNIQUE ID
# ============================================================
# HAR CUSTOMER KE LIYE ALAG APP/LINK BANATE WAQT
# YE ID CHANGE KARNA HAI.
#
# Customer 1 = RBL001
# Customer 2 = RBL002
# Customer 3 = RBL003
# ============================================================

SHOP_ID = "RBL001"


# ============================================================
# LICENSE SECRET
# ============================================================
# IMPORTANT:
# Secret yahan directly mat likhna.
#
# Streamlit Cloud:
# Settings -> Secrets
#
# Wahan:
#
# LICENSE_SECRET = "YOUR_LONG_RANDOM_SECRET"
#
# Pydroid ke generator mein bhi SAME secret hona chahiye.
# CUSTOMER KO SECRET KABHI MAT DENA.
# ============================================================

try:
    LICENSE_SECRET = st.secrets["LICENSE_SECRET"]
except Exception:
    st.error("License system configuration missing.")
    st.stop()


# ============================================================
# WORDS LOGIC
# ============================================================

ONES = [
    "",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
    "Eleven",
    "Twelve",
    "Thirteen",
    "Fourteen",
    "Fifteen",
    "Sixteen",
    "Seventeen",
    "Eighteen",
    "Nineteen"
]

TENS = [
    "",
    "",
    "Twenty",
    "Thirty",
    "Forty",
    "Fifty",
    "Sixty",
    "Seventy",
    "Eighty",
    "Ninety"
]


def number_to_words(n):

    n = int(n)

    if n == 0:
        return "Zero"

    if n < 20:
        return ONES[n]

    if n < 100:
        return (
            TENS[n // 10]
            + (" " + ONES[n % 10] if n % 10 else "")
        )

    if n < 1000:
        return (
            ONES[n // 100]
            + " Hundred"
            + (
                " " + number_to_words(n % 100)
                if n % 100
                else ""
            )
        )

    if n < 100000:
        return (
            number_to_words(n // 1000)
            + " Thousand"
            + (
                " " + number_to_words(n % 1000)
                if n % 1000
                else ""
            )
        )

    if n < 10000000:
        return (
            number_to_words(n // 100000)
            + " Lakh"
            + (
                " " + number_to_words(n % 100000)
                if n % 100000
                else ""
            )
        )

    return (
        number_to_words(n // 10000000)
        + " Crore"
        + (
            " " + number_to_words(n % 10000000)
            if n % 10000000
            else ""
        )
    )


def amount_in_words(amount):

    rupees = int(amount)

    paise = int(
        round((amount - rupees) * 100)
    )

    result = (
        number_to_words(rupees)
        + " Rupees"
    )

    if paise > 0:
        result += (
            " and "
            + number_to_words(paise)
            + " Paise"
        )

    return result + " Only"


# ============================================================
# INVOICE NUMBER
# ============================================================

def get_next_invoice_number():

    os.makedirs(
        "M_Saad_Bills",
        exist_ok=True
    )

    file = "M_Saad_Bills/invoice_counter.txt"

    try:

        if os.path.exists(file):

            with open(file, "r") as f:
                num = int(f.read())

        else:
            num = 0

    except Exception:
        num = 0

    num += 1

    with open(file, "w") as f:
        f.write(str(num))

    return (
        f"INV-{datetime.now().year}-"
        f"{num:05d}"
    )


# ============================================================
# LICENSE SYSTEM v2
# ============================================================

LICENSE_FILE = "license.txt"
INSTALL_FILE = "install_date.txt"

TRIAL_DAYS = 7


# ------------------------------------------------------------
# INSTALL DATE
# ------------------------------------------------------------

def get_install_date():

    if not os.path.exists(INSTALL_FILE):

        today = date.today()

        with open(INSTALL_FILE, "w") as f:
            f.write(str(today))

        return today

    try:

        with open(INSTALL_FILE, "r") as f:
            return date.fromisoformat(
                f.read().strip()
            )

    except Exception:

        return date.today()


install_date = get_install_date()

trial_days_left = (
    TRIAL_DAYS
    - (date.today() - install_date).days
)


# ------------------------------------------------------------
# CREATE LICENSE SIGNATURE
# ------------------------------------------------------------

def create_signature(
    shop_id,
    days,
    issue_date
):

    message = (
        f"{shop_id}|{days}|{issue_date}"
    )

    signature = hmac.new(
        LICENSE_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    return signature[:12].upper()


# ------------------------------------------------------------
# CHECK LICENSE
# ------------------------------------------------------------

def check_license():

    if not os.path.exists(LICENSE_FILE):

        if trial_days_left >= 0:

            return (
                True,
                trial_days_left,
                "Trial"
            )

        return (
            False,
            0,
            "Expired"
        )

    try:

        with open(
            LICENSE_FILE,
            "r"
        ) as f:

            expiry = date.fromisoformat(
                f.read().strip()
            )

        remaining = (
            expiry - date.today()
        ).days

        if remaining >= 0:

            return (
                True,
                remaining,
                "Licensed"
            )

    except Exception:
        pass

    return (
        False,
        0,
        "Expired"
    )


# ------------------------------------------------------------
# ACTIVATE LICENSE
# ------------------------------------------------------------

def activate_license(key):

    try:

        parts = (
            key.strip()
            .upper()
            .split("-")
        )

        # FORMAT:
        #
        # MSAAD-RBL001-30-20260917-XXXXXXXXXXXX
        #

        if len(parts) != 5:
            return False

        prefix = parts[0]
        shop_id = parts[1]
        days_text = parts[2]
        issue_date = parts[3]
        signature = parts[4]


        # Prefix
        if prefix != "MSAAD":
            return False


        # Customer ID
        if shop_id != SHOP_ID.upper():
            return False


        # Only 30 or 365 days
        if days_text not in (
            "30",
            "365"
        ):
            return False


        days = int(days_text)


        # Date format
        try:

            issue = datetime.strptime(
                issue_date,
                "%Y%m%d"
            ).date()

        except Exception:

            return False


        # Key age check
        difference = (
            date.today() - issue
        ).days

        # Allow current day + small clock difference
        if difference < -1 or difference > 31:
            return False


        # Recreate signature
        expected_signature = (
            create_signature(
                shop_id,
                days,
                issue_date
            )
        )


        # Secure comparison
        if not hmac.compare_digest(
            signature,
            expected_signature
        ):
            return False


        # Activate license
        expiry = (
            date.today()
            + timedelta(days=days)
        )


        with open(
            LICENSE_FILE,
            "w"
        ) as f:

            f.write(
                str(expiry)
            )


        return True


    except Exception:

        return False


# ============================================================
# LICENSE STATUS
# ============================================================

is_active, days_remaining, license_type = (
    check_license()
)


# ============================================================
# LICENSE SIDEBAR
# ============================================================

st.sidebar.title(
    "🔑 License Panel"
)


if is_active:

    if license_type == "Trial":

        st.sidebar.success(
            f"Trial: {days_remaining} Din Bache"
        )

    else:

        st.sidebar.success(
            f"Licensed: {days_remaining} Din"
        )

else:

    st.sidebar.error(
        "License Khatam"
    )


st.sidebar.write("---")


key_input = st.sidebar.text_input(
    "License Key",
    placeholder="MSAAD-RBL001-30-..."
)


if st.sidebar.button(
    "Activate Karo"
):

    if activate_license(
        key_input
    ):

        st.sidebar.success(
            "License Activated!"
        )

        st.rerun()

    else:

        st.sidebar.error(
            "Invalid License Key!"
        )


# ============================================================
# EXPIRED USER BLOCK
# ============================================================

if not is_active:

    st.error(
        "⏰ Trial / License Khatam Ho Gaya"
    )

    st.markdown(
        f"""
        ### {SELLER_NAME} - Subscription Lo

        **Monthly: ₹199**

        **Yearly: ₹1499**

        GPay: 7387246146
        """
    )

    st.link_button(
        "💳 Payment Karo",
        "https://razorpay.me/@royalclothing"
    )

    st.stop()


# ============================================================
# BILLING APP
# ============================================================

st.title(
    f"👑 {SELLER_NAME}"
)

st.caption(
    f"{SELLER_ADDRESS} | {SELLER_PHONE}"
)


# ============================================================
# CUSTOMER DETAILS
# ============================================================

st.subheader(
    "Customer Details"
)

c1, c2 = st.columns(2)


with c1:

    cust_name = st.text_input(
        "Customer Name",
        "Abutalha"
    )


with c2:

    cust_phone = st.text_input(
        "Phone",
        "1273275821"
    )


cust_addr = st.text_input(
    "Address",
    "AP road"
)


# ============================================================
# SUPPLY TYPE
# ============================================================

supply = st.radio(
    "Supply Type",
    [
        "Intra-State (CGST+SGST)",
        "Inter-State (IGST)"
    ],
    horizontal=True
)


supply_type = (
    "intra"
    if "Intra" in supply
    else "inter"
)


st.write("---")


# ============================================================
# ADD ITEM
# ============================================================

st.subheader(
    "Add Item"
)


ic1, ic2, ic3, ic4 = st.columns(4)


with ic1:

    iname = st.text_input(
        "Item Name"
    )


with ic2:

    iqty = st.number_input(
        "Qty",
        1,
        1000,
        1
    )


with ic3:

    iprice = st.number_input(
        "Price",
        0.0
    )


with ic4:

    igst = st.selectbox(
        "GST%",
        [0, 5, 12, 18, 28],
        index=2
    )


if st.button(
    "Add Item"
):

    if iname:

        st.session_state.bill_items.append(
            {
                "item": iname,
                "qty": iqty,
                "price": iprice,
                "gst": igst
            }
        )

        st.rerun()


# ============================================================
# DISCOUNT
# ============================================================

discount = st.number_input(
    "Discount Rs",
    0.0
)


# ============================================================
# SHOW ITEMS
# ============================================================

if st.session_state.bill_items:

    for idx, it in enumerate(
        st.session_state.bill_items
    ):

        st.write(
            f"{idx+1}. "
            f"{it['item']} - "
            f"{it['qty']} x "
            f"{it['price']} - "
            f"GST {it['gst']}%"
        )


# ============================================================
# CREATE PDF
# ============================================================

if st.button(
    "🧾 Royal PDF Banao"
):

    if not st.session_state.bill_items:

        st.warning(
            "Pehle item add karo"
        )

        st.stop()


    bill_no = get_next_invoice_number()


    class InvoicePDF(FPDF):


        def header(self):

            self.set_fill_color(
                15,
                32,
                64
            )

            self.rect(
                0,
                0,
                210,
                34,
                "F"
            )

            self.set_y(6)

            self.set_font(
                "helvetica",
                "B",
                18
            )

            self.set_text_color(
                255,
                215,
                0
            )

            self.cell(
                0,
                9,
                SELLER_NAME,
                align="C",
                ln=True
            )

            self.set_font(
                "helvetica",
                "",
                8
            )

            self.set_text_color(
                255,
                255,
                255
            )

            self.cell(
                0,
                5,
                SELLER_ADDRESS,
                align="C",
                ln=True
            )

            self.cell(
                0,
                5,
                f"Phone: {SELLER_PHONE} | Email: {SELLER_EMAIL}",
                align="C",
                ln=True
            )


        def footer(self):

            self.set_y(-18)

            self.set_font(
                "helvetica",
                "",
                8
            )

            self.set_text_color(
                100,
                100,
                100
            )

            self.cell(
                0,
                5,
                f"Thank you! | {MY_FOOTER}",
                align="C",
                ln=True
            )


    # ========================================================
    # PDF SETUP
    # ========================================================

    pdf = InvoicePDF()

    pdf.set_auto_page_break(
        auto=True,
        margin=20
    )

    pdf.add_page()

    pdf.set_y(40)


    # ========================================================
    # INVOICE NUMBER + DATE
    # ========================================================

    pdf.set_font(
        "helvetica",
        "B",
        10
    )

    pdf.set_text_color(
        15,
        32,
        64
    )

    pdf.cell(
        100,
        7,
        f"Invoice No: {bill_no}"
    )


    pdf.set_font(
        "helvetica",
        "",
        10
    )

    pdf.set_text_color(
        80,
        80,
        80
    )

    pdf.cell(
        0,
        7,
        f"Date: {datetime.now().strftime('%d-%m-%Y')}",
        align="R",
        ln=True
    )


    pdf.ln(4)


    # ========================================================
    # BILL TO
    # ========================================================

    pdf.set_fill_color(
        240,
        245,
        255
    )

    pdf.set_draw_color(
        180,
        190,
        210
    )

    y = pdf.get_y()

    pdf.rect(
        10,
        y,
        190,
        22,
        "DF"
    )


    pdf.set_xy(
        14,
        y + 3
    )

    pdf.set_font(
        "helvetica",
        "B",
        11
    )

    pdf.set_text_color(
        0,
        90,
        170
    )

    pdf.cell(
        0,
        6,
        f"BILL TO: {cust_name}",
        ln=True
    )


    pdf.set_font(
        "helvetica",
        "",
        9
    )

    pdf.set_text_color(
        60,
        60,
        60
    )

    pdf.set_x(14)

    pdf.cell(
        0,
        5,
        f"Phone: {cust_phone} | Address: {cust_addr}",
        ln=True
    )


    pdf.set_y(
        y + 26
    )


    # ========================================================
    # SUPPLY TYPE
    # ========================================================

    pdf.set_font(
        "helvetica",
        "B",
        10
    )

    pdf.set_text_color(
        15,
        32,
        64
    )

    if supply_type == "intra":

        pdf.cell(
            0,
            7,
            "Supply Type: Intra-State (CGST + SGST)",
            ln=True
        )

    else:

        pdf.cell(
            0,
            7,
            "Supply Type: Inter-State (IGST)",
            ln=True
        )


    pdf.ln(2)


    # ========================================================
    # TABLE
    # ========================================================

    col_widths = [
        48,
        18,
        28,
        22,
        24,
        45
    ]

    headers = [
        "Item",
        "Qty",
        "Price",
        "GST %",
        "Tax",
        "Amount"
    ]


    pdf.set_fill_color(
        15,
        32,
        64
    )

    pdf.set_text_color(
        255,
        215,
        0
    )

    pdf.set_font(
        "helvetica",
        "B",
        9
    )


    for i, h in enumerate(headers):

        pdf.cell(
            col_widths[i],
            9,
            h,
            border=1,
            align="C",
            fill=True
        )


    pdf.ln()


    # ========================================================
    # CALCULATIONS
    # ========================================================

    subtotal = 0.0
    total_gst = 0.0


    for idx, data in enumerate(
        st.session_state.bill_items
    ):

        base = (
            data["qty"]
            * data["price"]
        )

        tax = (
            base
            * (data["gst"] / 100.0)
        )

        subtotal += base
        total_gst += tax


        if idx % 2 == 0:

            pdf.set_fill_color(
                240,
                245,
                255
            )

        else:

            pdf.set_fill_color(
                255,
                255,
                255
            )


        pdf.set_font(
            "helvetica",
            "",
            9
        )

        pdf.set_text_color(
            20,
            20,
            20
        )


        pdf.cell(
            col_widths[0],
            8,
            data["item"][:28],
            border=1,
            align="C",
            fill=True
        )


        pdf.cell(
            col_widths[1],
            8,
            str(data["qty"]),
            border=1,
            align="C",
            fill=True
        )


        pdf.cell(
            col_widths[2],
            8,
            f"{data['price']:.2f}",
            border=1,
            align="C",
            fill=True
        )


        pdf.cell(
            col_widths[3],
            8,
            f"{data['gst']:g}%",
            border=1,
            align="C",
            fill=True
        )


        pdf.cell(
            col_widths[4],
            8,
            f"{tax:.2f}",
            border=1,
            align="C",
            fill=True
        )


        pdf.cell(
            col_widths[5],
            8,
            f"{base + tax:.2f}",
            border=1,
            align="C",
            fill=True
        )


        pdf.ln()


    # ========================================================
    # DISCOUNT + TAX
    # ========================================================

    taxable_value = (
        subtotal - discount
    )


    if taxable_value < 0:

        taxable_value = 0


    discount_ratio = (
        taxable_value / subtotal
        if subtotal > 0
        else 0
    )


    adjusted_gst = (
        total_gst * discount_ratio
        if subtotal > 0
        else 0
    )


    final_bill = (
        taxable_value
        + adjusted_gst
    )


    if supply_type == "intra":

        cgst = adjusted_gst / 2
        sgst = adjusted_gst / 2
        igst = 0

    else:

        cgst = 0
        sgst = 0
        igst = adjusted_gst


    # ========================================================
    # TOTAL SECTION
    # ========================================================

    pdf.ln(5)

    pdf.set_font(
        "helvetica",
        "",
        10
    )

    pdf.set_text_color(
        60,
        60,
        60
    )


    pdf.cell(
        135,
        7,
        "Subtotal:",
        align="R"
    )

    pdf.cell(
        0,
        7,
        f"Rs {subtotal:.2f}",
        align="R",
        ln=True
    )


    if discount > 0:

        pdf.set_text_color(
            180,
            60,
            20
        )

        pdf.cell(
            135,
            7,
            "Discount:",
            align="R"
        )

        pdf.cell(
            0,
            7,
            f"- Rs {discount:.2f}",
            align="R",
            ln=True
        )


    pdf.set_text_color(
        60,
        60,
        60
    )


    pdf.cell(
        135,
        7,
        "Taxable Value:",
        align="R"
    )

    pdf.cell(
        0,
        7,
        f"Rs {taxable_value:.2f}",
        align="R",
        ln=True
    )


    if supply_type == "intra":

        pdf.cell(
            135,
            7,
            "CGST:",
            align="R"
        )

        pdf.cell(
            0,
            7,
            f"Rs {cgst:.2f}",
            align="R",
            ln=True
        )


        pdf.cell(
            135,
            7,
            "SGST:",
            align="R"
        )

        pdf.cell(
            0,
            7,
            f"Rs {sgst:.2f}",
            align="R",
            ln=True
        )

    else:

        pdf.cell(
            135,
            7,
            "IGST:",
            align="R"
        )

        pdf.cell(
            0,
            7,
            f"Rs {igst:.2f}",
            align="R",
            ln=True
        )


    # ========================================================
    # TOTAL GST
    # ========================================================

    pdf.set_text_color(
        200,
        80,
        0
    )

    pdf.set_font(
        "helvetica",
        "B",
        10
    )


    pdf.cell(
        135,
        7,
        "Total GST:",
        align="R"
    )

    pdf.cell(
        0,
        7,
        f"Rs {adjusted_gst:.2f}",
        align="R",
        ln=True
    )


    # ========================================================
    # FINAL PAYABLE
    # ========================================================

    pdf.ln(3)

    pdf.set_fill_color(
        15,
        32,
        64
    )

    pdf.set_text_color(
        255,
        215,
        0
    )

    pdf.set_font(
        "helvetica",
        "B",
        13
    )


    pdf.cell(
        135,
        12,
        "FINAL PAYABLE:",
        align="R",
        fill=True
    )

    pdf.cell(
        0,
        12,
        f"Rs {final_bill:.2f}",
        align="R",
        fill=True,
        ln=True
    )


    # ========================================================
    # AMOUNT IN WORDS
    # ========================================================

    pdf.ln(4)

    pdf.set_font(
        "helvetica",
        "B",
        9
    )

    pdf.set_text_color(
        15,
        32,
        64
    )

    pdf.cell(
        0,
        6,
        "Amount in Words:",
        ln=True
    )


    pdf.set_font(
        "helvetica",
        "",
        9
    )

    pdf.set_text_color(
        60,
        60,
        60
    )

    pdf.multi_cell(
        0,
        5,
        amount_in_words(final_bill)
    )


    # ========================================================
    # SAVE PDF
    # ========================================================

    pdf.output(
        "bill.pdf"
    )


    with open(
        "bill.pdf",
        "rb"
    ) as f:

        st.download_button(
            "📥 Download Royal Bill",
            f,
            file_name=(
                f"{cust_name}_{bill_no}.pdf"
            )
        )


# ============================================================
# CLEAR ALL
# ============================================================

if st.button(
    "Clear All"
):

    st.session_state.bill_items = []

    st.rerun()