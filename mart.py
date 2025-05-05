import streamlit as st
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

# --- Branding & Header ---
st.set_page_config(page_title="MiniMart", page_icon="🛒", layout="centered")
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image("mm.png", width=150)
    st.markdown("## 🛍️ MiniMart")
    st.markdown("### 🍏 Fresh & Fast")

# st.markdown("""
#     <div style='text-align: center;'>
#         <h1 style='color: green;'> MiniMart</h1>
#         <h3 style='color: gray;'>Fresh & Fast</h3>
#     </div>
# """, unsafe_allow_html=True)

# --- Prices ---
PRICES = {
    "Pizza": 350, "Burger": 120, "Cold Drink": 150,
    "Lassi": 80, "Fresh Juice": 100, "Tea": 40,
    "Samosa": 30, "French Fries": 70, "Nuggets": 100,
    "Almonds": 200, "Cashew Nuts": 250,
    "Russian Salad": 150, "Green Salad": 90,
    "Mango Pickle": 50, "Mixed Pickle": 60,
    "Birthday Cake": 500
}

# --- Session State Initialization ---
if 'order' not in st.session_state:
    st.session_state['order'] = {item: 0 for item in PRICES}
if 'confirmed' not in st.session_state:
    st.session_state['confirmed'] = False

# --- Sidebar: Customer Info ---
st.sidebar.header("🧑‍💼 Customer Info")
customer_name = st.sidebar.text_input("Enter your name:")

# --- Sidebar: Delivery Option ---
st.sidebar.markdown("🚚 **Delivery Options**")
delivery_method = st.sidebar.radio("Select Delivery Method:", ("Pickup from Store", "Home Delivery"))

delivery_charge = 0
cell_number = ""
delivery_address = ""

if delivery_method == "Home Delivery":
    delivery_charge = 100
    cell_number = st.sidebar.text_input("📞 Enter Cell Phone Number:")
    delivery_address = st.sidebar.text_area("🏠 Enter Delivery Address:")
    if not delivery_address:
        st.sidebar.warning("Please provide your address for home delivery.")

# --- Order Time ---
order_time = datetime.now().strftime("%d-%m-%Y %I:%M %p")

# --- Item Selection ---
st.markdown("""
    <div style='text-align: center;'>
        <h1 style='color: white;'>Select Your Items📜</h1>
    </div>
""", unsafe_allow_html=True)
# st.header("📜 Select Your Items")
def item_selector(title, items):
    st.subheader(title)
    for item in items:
        st.session_state['order'][item] = st.number_input(
            f"{item} (Rs. {PRICES[item]})", min_value=0, max_value=10, step=1, key=item
        )
        
item_selector("🍕 Fast Food", ["Pizza", "Burger", "Cold Drink"])
item_selector("🥤 Drinks", ["Lassi", "Fresh Juice", "Tea"])
item_selector("🍟 Snacks", ["Samosa", "French Fries", "Nuggets"])
item_selector("🥜 Dry Fruits", ["Almonds", "Cashew Nuts"])
item_selector("🥗 Salads", ["Russian Salad", "Green Salad"])
item_selector("🥒 Pickles", ["Mango Pickle", "Mixed Pickle"])
item_selector("🎂 Birthday Special", ["Birthday Cake"])

# --- Place Order ---
if st.button("\u2705 Place Order"):
    total_qty = sum(st.session_state['order'].values())
    if not customer_name:
        st.warning("Please enter your name in the sidebar.")
    elif delivery_method == "Home Delivery" and (not delivery_address or not cell_number):
        st.warning("Please enter delivery address and cell number.")
    elif total_qty == 0:
        st.warning("Please select at least 1 item.")
    elif total_qty > 10:
        st.error("\u26a0\ufe0f Maximum 10 items allowed per order.")
    else:
        st.session_state['confirmed'] = True
        st.success("\u2705 Your order has been placed!")

# --- Reset Order ---
if st.button("\u267b\ufe0f Reset"):
    st.session_state['order'] = {item: 0 for item in PRICES}
    st.session_state['confirmed'] = False
    st.experimental_set_query_params()  # Optional refresh
    st.rerun()  # Safe rerun after reset (for supported versions)
# --- Reset button logic ---
# --- Generate PDF Receipt ---
if st.session_state['confirmed']:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 50
    line_height = 20

    # Logo
    pdf.drawImage("mm.png", 40, y - 40, width=60, height=60)
    y -= 70

    # Header
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(150, y, "MiniMart Receipt")
    y -= 2 * line_height

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Customer Name: {customer_name}")
    y -= line_height
    if cell_number:
        pdf.drawString(50, y, f"Phone: {cell_number}")
        y -= line_height
    pdf.drawString(50, y, f"Date & Time: {order_time}")
    y -= 2 * line_height

    pdf.drawString(50, y, "Item")
    pdf.drawString(250, y, "Qty")
    pdf.drawString(350, y, "Price")
    y -= line_height
    pdf.line(50, y, 500, y)
    y -= line_height

    total_amount = delivery_charge
    for item, qty in st.session_state['order'].items():
        if qty > 0:
            price = PRICES[item] * qty
            pdf.drawString(50, y, item)
            pdf.drawString(250, y, str(qty))
            pdf.drawString(350, y, f"Rs. {price}")
            total_amount += price
            y -= line_height

    if delivery_method == "Home Delivery":
        y -= line_height
        pdf.drawString(50, y, f"Delivery Address: {delivery_address}")
        y -= line_height
        pdf.drawString(50, y, f"Delivery Charges: Rs. {delivery_charge}")
        y -= line_height

    y -= line_height
    pdf.drawString(50, y, f"Total Amount: Rs. {total_amount}")
    y -= 2 * line_height
    pdf.drawString(50, y, "Thanks for shopping with us!")
    y -= 2 * line_height
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, y, "\ud83c\udf6d MiniMart - Fresh & Fast")
    y -= line_height
    pdf.drawString(50, y, "Email: omprince31@gmail.com | Phone: +92-349-3738149")

    pdf.save()
    buffer.seek(0)

    st.download_button(
        label="Download Invoice (PDF)",
        data=buffer,
        file_name=f"Invoice_{customer_name or 'Customer'}.pdf",
        mime="application/pdf"
    )

# --- Footer ---
st.markdown("---")
st.markdown("♡ Made with \u2764\ufe0f by **MiniMart Team** | ☎️ Contact: minimart@example.com", unsafe_allow_html=True)
st.markdown("💬 WhatsApp: +92-342-3471098")
st.markdown("➤ Follow us on 📸 [Instagram](https://www.instagram.com/minimart) | ⓕ [Facebook](https://www.facebook.com/minimart)")
st.markdown("🌐 Visit our website: [www.minimart.com](https://www.minimart.com)")
st.write("✓ since \u00a9 2025 My Portfolio. All rights reserved.")
# # --- Streamlit App ---