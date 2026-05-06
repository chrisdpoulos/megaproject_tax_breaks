# Streamlit app to calcuate the tax break 
# 
# for a megaproject in Illinois. 
# The app will allow users to select a district and a megaproject example, 
# and then it will calculate how much the school district would lose in 
# property tax revenue as a result of the megaproject incentive bill.

# Created by: Christopher Poulos, Public Finance Analyst, Chicago Teachers Union
# Contact: christopherpoulos@ctulocal1.org

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import io

# Streamlit app title
def main():    

    # Set page configuration

    st.set_page_config(
        page_title="IL Megaproject Taxbreak Calculator", 
        layout="centered",
        page_icon="💰",
        initial_sidebar_state="expanded"
    )

    # Title

    st.markdown("""<h1>Illinois Megaproject - Mega Loss Calculator</h1>""",unsafe_allow_html=True)

    st.markdown("""<p>As-written, the Mega Project bill rewrites the tax code for the State of Illinois and signifies the largest transfer of responsibility for revenue for local revenue, schools, and services from private developers to individual property owners in the state’s history.

To understand the impact of the proposed mega project bill, use the calculator below.
</p>""",unsafe_allow_html=True)

    st.markdown("""<h2>Step 1. Adjust your local tax rate.</h2>""",unsafe_allow_html=True)
    tax_rate_pct = st.slider("",min_value=1.00,max_value=20.00,value=9.48,step=0.01,format="%0.2f%%",help="You can find your total local tax rate on your property tax bill, which can be found online on the Cook County Treasurer's website: https://www.cookcountytreasurer.com/setsearchparameters.aspx.")
    tax_rate = tax_rate_pct / 100

    st.markdown("""<h2>Step 2. Select your county.</h2>""",unsafe_allow_html=True)

    counties = [ "ADAMS", "ALEXANDER", "BOND", "BOONE", "BROWN", "BUREAU", "CALHOUN", "CARROLL", "CASS", "CHAMPAIGN", "CHRISTIAN", "CLARK", "CLAY", "CLINTON", "COLES", "COOK", "CRAWFORD", "CUMBERLAND", "DEKALB", "DEWITT", "DOUGLAS", "DUPAGE", "EDGAR", "EDWARDS", "EFFINGHAM", "FAYETTE", "FORD", "FRANKLIN", "FULTON", "GALLATIN", "GREENE", "GRUNDY", "HAMILTON", "HANCOCK", "HARDIN", "HENDERSON", "HENRY", "IROQUOIS", "JACKSON", "JASPER", "JEFFERSON", "JERSEY", "JO DAVIESS", "JOHNSON", "KANE", "KANKAKEE", "KENDALL", "KNOX", "LAKE", "LASALLE", "LAWRENCE", "LEE", "LIVINGSTON", "LOGAN", "MACON", "MACOUPIN", "MADISON", "MARION", "MARSHALL", "MASON", "MASSAC", "MCDONOUGH", "MCHENRY", "MCLEAN", "MENARD", "MERCER", "MONROE", "MONTGOMERY", "MORGAN", "MOULTRIE", "OGLE", "PEORIA", "PERRY", "PIATT", "PIKE", "POPE", "PULASKI", "PUTNAM", "RANDOLPH", "RICHLAND", "ROCK ISLAND", "SALINE", "SANGAMON", "SCHUYLER", "SCOTT", "SHELBY", "ST CLAIR", "STARK", "STEPHENSON", "TAZEWELL", "UNION", "VERMILION", "WABASH", "WARREN", "WASHINGTON", "WAYNE", "WHITE", "WHITESIDE", "WILL", "WILLIAMSON", "WINNEBAGO", "WOODFORD" ]

    county = st.selectbox("", counties, index=15)

    st.markdown("""<h2>Step 3. Select a sample megaproject or enter a custom amount.</h2>""",unsafe_allow_html=True)

    # Select megaproject
    project = st.radio("", ["Google HQ","McCaskeys’ Stadium for the Bears and Entertainment Center","Enter Custom Amount"],index=2)
    if project == "Enter Custom Amount":
        project_amount = st.number_input(
            "Or enter a custom megaproject amount ($)",
            min_value=100_000_000,
            value=280_000_000,
            step=10_000_000,
            format="%d",
            help="Enter whole dollars only."
        )
        st.caption(f"Custom amount selected: ${int(project_amount):,}")

    # Set special payment percentage

    special_payment_percentage = .1

    # Inflation - 103% (liberal estimate. According to the Congressional Budget Office's An Update to the Budget and Economic Outlook: 2024 to 2034 (https://www.cbo.gov/publication/60419) the 10 year inflation average is 2%)
    
    inflation = 1.03

    # Set added equalized assesseed value (assuming added EAV equals the full proposed project cost amount) - (Value * Assessed Value (for commerical) * equalization factor).
    # Most recent equalization factor is for 2025 (https://tax.illinois.gov/research/news/2024-cook-county-final-multiplier.html)

    if county ==  "COOK":
        google_hq = (280000000*.25*3.0355)
        bears = (2000000000*.25*3.0355)
        if project == "Enter Custom Amount":
            custom = (project_amount*.25*3.0355)
    else:
        google_hq = (280000000*.25*3.0355)
        bears = (2000000000*.25*3.0355)
        if project == "Enter Custom Amount":
            custom = (project_amount*.25*3.0355)

    if project == "Google HQ":

        # Initial project variables

        project_cost = 280000000
        base_eav =  26249106  # Based on 2025 Assessor certified value of parcels found using maps.cookcountyil.gov. PINs: 17-09-434-024-0000, 17-09-434-021-0000, 17-09-434-022-0000, and 17-09-434-023-00000
        tax_break_term = 25
        special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
        value_added_y1 = google_hq
        project_name = "Google HQ"

        # Tax break calculations

        if county ==  "COOK":
            df_project = pd.DataFrame({
                "Year": list(range(1,26)),
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 26)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
            df_project["Tax Rate"] = tax_rate
        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,26)),
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 26)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
            df_project["Tax Rate"] = tax_rate


    elif project == "McCaskeys’ Stadium for the Bears and Entertainment Center":

        # Initial project variables

        project_cost = 2000000001
        base_eav = 13042965
        tax_break_term = 40
        special_payment_percentage = 0 # SPECIAL PAYMENT NOT REQUIRED 35 ILCS 200/10-1025(a) (line 22-23) https://ilga.gov/documents/legislation/104/HB/PDF/10400HB0910lv.pdf
        special_payment_min = special_payment_percentage*(base_eav*tax_rate) # Assume 100% special payment
        value_added_y1 = bears
        project_name = "McCaskeys’ Stadium for the Bears and Entertainment Center"
        
        # Tax break calculations

        if county ==  "COOK":
            df_project = pd.DataFrame({
                "Year": list(range(1,41)),
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 41)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
            df_project["Tax Rate"] = tax_rate
        else:
            df_project = pd.DataFrame({
                "Year": list(range(1,41)),
                "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 41)]
            })
            df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
            df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
            df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
            df_project["Tax Rate"] = tax_rate

    elif project == "Enter Custom Amount":

        # Initial project variables
        value_added_y1 = custom
        project_name = "Your custom megaproject"
        project_cost = project_amount

        if project_amount >= 100_000_000 and project_amount <= 500_000_000:
            base_eav = project_amount*.2 # Assigning 20% of project cost to acquistion amount
            tax_break_term = 25
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
        # Tax break calculations

            if county ==  "COOK":
                df_project = pd.DataFrame({
                    "Year": list(range(1,26)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 26)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
                df_project["Tax Rate"] = tax_rate
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,26)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,26)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,26)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 26)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
                df_project["Tax Rate"] = tax_rate
        if project_amount > 500_000_000 and project_amount <= 1_000_000_000:
            base_eav = project_amount*.2 # Assigning 20% of project cost to acquistion amount
            tax_break_term = 30
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            
            # Tax break calculations

            if county ==  "COOK":
                df_project = pd.DataFrame({
                    "Year": list(range(1,31)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,31)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 31)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
                df_project["Tax Rate"] = tax_rate
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,31)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,31)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,31)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 31)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
                df_project["Tax Rate"] = tax_rate
        if project_amount > 1_000_000_000 and project_amount <= 2_000_000_000:
            base_eav = project_amount*.2 # Assigning 20% of project cost to acquistion amount
            tax_break_term = 40
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            
            # Tax break calculations

            if county ==  "COOK":
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 41)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
                df_project["Tax Rate"] = tax_rate
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 41)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
                df_project["Tax Rate"] = tax_rate
        if project_amount > 2_000_000_000:
            base_eav = project_amount*.2 # Assigning 20% of project cost to acquistion amount
            tax_break_term = 40
            special_payment_percentage = 0
            special_payment_min = special_payment_percentage * (base_eav*tax_rate) # Assume 100% special payment
            # Tax break calculations

            if county ==  "COOK":
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 3) for year in range(1, 41)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
                df_project["Tax Rate"] = tax_rate
            else:
                df_project = pd.DataFrame({
                    "Year": list(range(1,41)),
                    "Special Payment": [special_payment_min*inflation ** (year-1) for year in range(1,41)],
                    "Tax Break Nominal": [value_added_y1 for year in range(1,41)],
                    "Tax Break EAV Adjusment": [value_added_y1 * 1.04 ** ((year - 1) // 4) for year in range(1, 41)]
                })
                df_project['Tax Break Cumulative'] = (df_project['Tax Break EAV Adjusment'].cumsum()-df_project['Special Payment'].cumsum())
                df_project['Special Payment Cumulative'] = df_project['Special Payment'].cumsum()
                df_project["Tax Break After Special Payment"] = df_project["Tax Break Cumulative"] - df_project["Special Payment Cumulative"]
                df_project["Tax Rate"] = tax_rate
    # Overview

    special_payment_total = df_project["Special Payment Cumulative"].values[-1]
    tax_break_total = df_project["Tax Break Cumulative"].values[-1]
    tax_break_total_schools = tax_break_total/2
    tax_break_year1 = df_project["Tax Break Cumulative"].values[0]
    tax_break_year1_schools = tax_break_year1/2
    special_payment_ratio = (special_payment_total / tax_break_total) if tax_break_total else 0

    if project == "Enter Custom Amount":
        st.markdown(f"""<h3>Without the Mega Project bill's tax gifts to developers, your city or town would receive an additional <b><font size="6"; color="green">${tax_break_year1:,.0f}</b></font> in the first year of the project, and schools would receive <b><font size="6"; color="green">${tax_break_year1_schools:,.0f}.</b></font></h3>

<h3>But the Mega Project bill removes those funds from local revenue. Over the {tax_break_term} year tax break, <b><font size="6"; color="red">${tax_break_total:,.0f}</b></font> would stay in developers’ pockets instead of funding your city or town’s needs. Schools would lose <b><font size="6"; color="red">${tax_break_total:,.0f}</b></font> in funds from the project.</h3>
""",unsafe_allow_html=True,help="Special payment is a payment in lieu of the owner avoiding taxes. It applies to projects under $2 billion and is equal to 10% of the property tax revenue generated by the project area the 'base year', which is the year prior to the calednar year in which the megaproject is awarded a tax expenditure.")
    else:
        st.markdown(f"""<h3>Without the Mega Project bill's tax gifts to developers, your city or town would receive an additional <b><font size="6"; color="green">${tax_break_year1:,.0f}</b></font> in the first year of the project, and schools would receive <b><font size="6"; color="green">${tax_break_year1_schools:,.0f}.</b></font></h3>

<h3>But the Mega Project bill removes those funds from local revenue. Over the {tax_break_term} year tax break, <b><font size="6"; color="red">${tax_break_total:,.0f}</b></font> would stay in developers’ pockets instead of funding your city or town’s needs. Schools would lose <b><font size="6"; color="red">${tax_break_total:,.0f}</b></font> in funds from the project.</h3>
""",unsafe_allow_html=True,help="Special payment is a payment in lieu of the owner avoiding taxes. It applies to projects under $2 billion and is equal to 10% of the property tax revenue generated by the project area the 'base year', which is the year prior to the calednar year in which the megaproject is awarded a tax expenditure.")
    
#   st.markdown(f"""<p style="text-align: center;">Download our data and calculations to enter your own assumptions</p>""",unsafe_allow_html=True)

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        df_project.to_excel(writer, index=False, sheet_name="Tax Break Data")
        
    buffer.seek(0)

    _, download_col, _ = st.columns([1, 2, 1])
    with download_col:
        st.download_button(
            label="Download Data and Calculations",
            data=buffer,
            file_name="data.xlsx",
            mime="application/vnd.ms-excel",
            icon=":material/download:",
            help="The excel file contains the underlying data used to perform the calculations and steps to replicating our math."
        )

    st.markdown(f"""<sub>
This calculator was built by the Illinois Federation of Teachers based on our best reading of the HB0910 Mega Project bill as-written to help municipalities, school districts, and the general public better understand the sweeping changes and impacts of the bill being rushed forward.  If you have any questions, comments, or concerns regarding the calculations, asssumptions, or data, please contact us as christopherpoulos@ctulocal1.org.  
</sub>
""",unsafe_allow_html=True)


    st.subheader(f"Cumulative tax break over time")
    
# Animated chart

    base = df_project[["Year", "Tax Break Cumulative", "Special Payment Cumulative"]].copy()
    chart_data = base.melt(
        id_vars="Year",
        value_vars=["Tax Break Cumulative", "Special Payment Cumulative"],
        var_name="Category",
        value_name="Amount"
    )

    frames = []
    for t in base["Year"]:
        temp = chart_data.copy()
        temp["Frame"] = t
        temp["Amount Displayed"] = temp.apply(
            lambda r: r["Amount"] if r["Year"] <= t else 0,
            axis=1
        )
        frames.append(temp)

    anim_chart_data = pd.concat(frames, ignore_index=True)

    fig = px.bar(
        anim_chart_data,
        x="Year",
        y="Amount Displayed",
        color="Category",
        animation_frame="Frame",
        barmode="group",
        labels={"Amount Displayed": "Cumulative Amount", "Year": "Year", "Category": "", "Frame": "Year"}
    )

    fig.update_layout(transition={"duration": 400}, xaxis={"dtick": 1}, legend=dict(y=1.1,orientation='h'))
    fig.update_yaxes(autorange=True, tickprefix="$", separatethousands=True)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""<sub><b>Notes:</b></sub>

<sub>1. The current legislation requires a so-called "special payment" (this is a payment in lieu of the owner paying full taxes) equal to 10% of the base year property tax revenue adjusted for inflation.</sub>

<sub><b>Sources:</b></sub>
<ul>
<sub><li>School district equalized assessed value and tax rate data - Illinois Report Card SY2025, Illinois School Board of Education.</li></sub>
<sub><li>Megaproject legislation on termination dates and special assessments - <a href="https://ilga.gov/documents/legislation/104/HB/PDF/10400HB0910lv.pdf">HB0910</a>.</li></sub>
</ul>
""",unsafe_allow_html=True)

#    df_project_year = df_project[df_project["Year"] == year_value]    

#    st.markdown(f"The tax break for year {year_value} is \${df_project.loc[df_project['Year'] == year_value, "Tax Break After Special Payment"].values[0]:,.0f}.")

if __name__ == "__main__":
    main()
