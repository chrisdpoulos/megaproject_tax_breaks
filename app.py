# Streamlit app to calcuate the tax break for a megaproject in Illinois. 
# The app will allow users to select a district and a megaproject example, 
# and then it will calculate how much the school district would lose in 
# property tax revenue as a result of the megaproject incentive bill.

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px

# TODO: add county into df so I can create assessment rate and equalization factor for cook. (confirm these only apply to cook).abs


# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data.csv')
        df = df[df['Level']=="District"]
        df = df[["RCDTS","District","County","$ Total School Tax Rate per $100","$ EAV per Pupil","# School Enrollment "]]
        # remove end space from "# School Enrollment "
        df.columns = df.columns.str.strip()
        df['EAV'] = df["$ EAV per Pupil"] * df["# School Enrollment"]
        df = df.dropna()
        return df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}. Please ensure the CSV files are in the correct location.")
#        return None
        return None

# Streamlit app title
def main():    

    # Set page configuration

    st.set_page_config(
        page_title="IL Megaproject Taxbreak Calculator", 
        layout="centered",
        page_icon="💰",
        initial_sidebar_state="expanded"
    )

    # Load data

    df = load_data()
    if df is None:
        return

#####################################################################################################################################################
### SIDEBAR #########################################################################################################################################
#####################################################################################################################################################

    st.sidebar.header("Select a district and megaproject example to see how much your school would lose.")
    
    # Select district
    district = st.sidebar.selectbox("Select a district", df["District"].unique())

    df_district = df[df["District"] == district]

    # Create a variable for selected district's property tax rate and eav

    tax_rate = (df_district["$ Total School Tax Rate per $100"].values[0] / 100) # NOTE: This is a conservativer assumption since commercial tax rates are higher than residential. 
    eav = df_district["EAV"].values[0]

    # Select megaproject
    project = st.sidebar.radio("Select a megaproject example", ["A","B","Bears Stadium and Entertainment Center"])

    # Set special payment percentage

    special_payment_percentage = 2
    
    # Set added equalized assesseed value (assuming added EAV equals the full proposed project cost amount) - (Value * Assessed Value (for commerical) * equalization factor).
    # Most recent equalization factor is for 2025 (https://tax.illinois.gov/research/news/2024-cook-county-final-multiplier.html)

    if df_district['County'].values[0] ==  "Cook":
        a = (100000000*.25*3.0355)
        b = (500000000*.25*3.0355)
        bears = (2000000000*.25*3.0355)
    else:
        a = (100000000*.3333*1)
        b = (500000000*.3333*1)
        bears = (2000000000*.3333*1)

    if project == "A":
        project_cost = 100000000
        tax_break_term = 25
        special_payment_min = special_payment_percentage * (eav*tax_rate) # Assume 100% special payment
        value_added_y1 = a
        project_name = "A"
        if df_district['County'].values[0] ==  "Cook":
            df_project = pd.DataFrame({
                "Year": list(range(1,26)),
                "Special Payment": [special_payment_min for year in range(1,26)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.4 ** ((year - 1) // 3) for year in range(1, 26)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,26)),
                "Special Payment": [special_payment_min for year in range(1,26)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.4 ** ((year - 1) // 4) for year in range(1, 26)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]

    if project == "B":
        project_cost = 500000000
        tax_break_term = 30
        special_payment_min = special_payment_percentage * (eav*tax_rate) # Assume 100% special payment
        value_added_y1 = b
        project_name = "B"
        if df_district['County'].values[0] ==  "Cook":
            df_project = pd.DataFrame({
                "Year": list(range(1,31)),
                "Special Payment": [special_payment_min for year in range(1,31)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.4 ** ((year - 1) // 3) for year in range(1,31)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]

        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,31)),
                "Special Payment": [special_payment_min for year in range(1,31)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.4 ** ((year - 1) // 4) for year in range(1,31)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]


    elif project == "Bears Stadium and Entertainment Center":
        project_cost = 2000000000
        tax_break_term = 40
        special_payment_min = special_payment_percentage*0# SPECIAL PAYMENT NOT REQUIRED 35 ILCS 200/10-1025(a) (line 22-23) https://ilga.gov/documents/legislation/104/HB/PDF/10400HB0910lv.pdf
        value_added_y1 = bears
        project_name = "Bears Stadium and Entertainment Center"
        if df_district['County'].values[0] ==  "Cook":
            df_project = pd.DataFrame({
                "Year": list(range(1,41)),
                "Special Payment": [special_payment_min for year in range(1,41)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.4 ** ((year - 1) // 3) for year in range(1,41)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]

        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,41)),
                "Special Payment": [special_payment_min for year in range(1,41)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.4 ** ((year - 1) // 4) for year in range(1,41)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]

    

#####################################################################################################################################################
### MAIN ############################################################################################################################################
#####################################################################################################################################################

    # Title

    st.title("Illinois Megaproject Taxbreak Calculator")

    # Overview

    st.subheader(f"How much would a project like the {project_name} cost your school district?")

    st.markdown(f"""{project_name} is a \${project_cost:,.0f} megaproject. This makes it eligible for a {tax_break_term} year tax break.""")

    st.markdown(f"""This would cost your district \${df_project['Tax Break'].values[-1]:,.0f} over the {tax_break_term} year period and \${df_project['Tax Break'].values[0]:,.0f} in the first year alone.<sup>1</sup>""",unsafe_allow_html=True
)
    st.subheader(f"Cumulative tax break over time")

    # Example: values you already computed in df_project
    # columns: Year, Tax Break
    base = df_project[["Year", "Tax Break"]].copy()

    # Build animated long data:
    # for each frame year t, show bars for years 1..t
    frames = []
    for t in base["Year"]:
        temp = base.copy()
        temp["Frame"] = t
        temp["Displayed"] = temp.apply(
            lambda r: r["Tax Break"] if r["Year"] <= t else 0,
            axis=1
        )
        frames.append(temp)

    anim_df = pd.concat(frames, ignore_index=True)

    fig = px.bar(
        anim_df,
        x="Year",
        y="Displayed",
        animation_frame="Frame",
        range_y=[0, base["Tax Break"].max() * 1.1],
        labels={"Displayed": "Tax Break", "Frame": "Year"}
    )

    fig.update_layout(
        transition={"duration": 400},
        xaxis={"dtick": 1}
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""<sub><b>Notes:</b></sub>

<sub>1. Assumes a special payment of 100% of the tax revenue the year preceding the development. This is a liberal assumption. The current legislation requires a floor of 10%, which can be negotiated.

<sub><b>Sources:</b></sub>
<ul>
<sub><li>School district equalized assessed value and tax rate data - Illinois Report Card SY2025, Illinois School Board of Education.</li></sub>
<sub><li>Megaproject legislation on termination dates and special assessments - <a href="https://ilga.gov/documents/legislation/104/HB/PDF/10400HB0910lv.pdf">HB0910</a>.</li></sub>
</ul>
""",unsafe_allow_html=True)

#    df_project_year = df_project[df_project["Year"] == year_value]    

#    st.markdown(f"The tax break for year {year_value} is \${df_project.loc[df_project['Year'] == year_value, 'Tax Break'].values[0]:,.0f}.")

if __name__ == "__main__":
    main()
