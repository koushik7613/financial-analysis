import streamlit as st
import pandas as pd
from PIL import Image
import pytesseract

# Function to clean column names (remove spaces & lowercase)
def clean_column_names(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")  # Convert to lowercase & remove spaces
    return df

# Function to extract text from image using OCR
def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text

# Function to parse extracted text into a DataFrame
def parse_balance_sheet(text):
    # Split the text into lines and process
    lines = text.split('\n')
    data = []
    for line in lines:
        # Assuming the format is "Company, Total Liabilities, Total Equity, Net Income, Total Assets"
        if line.strip():  # Ignore empty lines
            parts = line.split(',')
            if len(parts) == 5:  # Ensure we have all required fields
                data.append({
                    "company": parts[0].strip(),
                    "total_liabilities": float(parts[1].strip()),
                    "total_equity": float(parts[2].strip()),
                    "net_income": float(parts[3].strip()),
                    "total_assets": float(parts[4].strip())
                })
    return pd.DataFrame(data)

# Function to analyze balance sheet
def analyze_balance_sheet(df, sheet_name):
    st.subheader(f"📊 Financial Analysis Report - {sheet_name}")

    # Clean column names to match expected format
    df = clean_column_names(df)

    # Check if required columns exist
    required_columns = ["total_liabilities", "total_equity", "net_income", "total_assets", "company"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"⚠️ Missing columns in {sheet_name}: {', '.join(missing_columns)}. Please check your images.")
        return None

    # Calculate Key Financial Ratios
    df["debt_to_equity_ratio"] = df["total_liabilities"] / df["total_equity"]
    df["return_on_assets"] = df["net_income"] / df["total_assets"]
    df["current_ratio"] = df["total_assets"] / df["total_liabilities"]

    # Display Analysis
    st.write(f"### 🏦 Key Financial Ratios ({sheet_name}):")
    st.dataframe(df[["company", "debt_to_equity_ratio", "return_on_assets", "current_ratio"]])

    # Determine Best Company
    best_company = df.sort_values(by="return_on_assets", ascending=False).iloc[0]
    st.success(f"🏆 Best Investment Option in {sheet_name}: **{best_company['company']}** with a Return on Assets of {best_company['return_on_assets']:.2f}")

    return best_company

# Streamlit UI
st.title("📈 Financial Analysis of Companies from Balance Sheet Images")

# Step 1: Upload Balance Sheet Images
st.sidebar.header("Upload Balance Sheet Images")
uploaded_files = st.sidebar.file_uploader("Upload balance sheet images", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    best_companies = []

    # Process each uploaded image
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        st.image(image, caption=f"Uploaded Image: {uploaded_file.name}", use_column_width=True)

        # Extract text from the image
        extracted_text = extract_text_from_image(image)
        st.write("### Extracted Text:")
        st.text(extracted_text)

        # Parse the extracted text into a DataFrame
        df = parse_balance_sheet(extracted_text)
        st.write(f"### 📜 Balance Sheet Data from {uploaded_file.name}")
        st.dataframe(df)

        # Analyze the balance sheet
        best_company = analyze_balance_sheet(df, uploaded_file.name)
        if best_company is not None:
            best_companies.append(best_company)

    # Display overall best company if multiple images are processed
    if best_companies:
        overall_best_company = pd.DataFrame(best_companies)
        overall_best_company = overall_best_company.sort_values(by="return_on_assets", ascending=False).iloc[0]
        st.success(f"🏆 Overall Best Investment Option: **{overall_best_company['company']}** with a Return on Assets of {overall_best_company['return_on_assets']:.2f}")

st.info("🔹 Upload images of balance sheets to start the analysis.")