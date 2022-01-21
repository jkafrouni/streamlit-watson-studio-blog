import streamlit as st
import cpd_helpers
import plotly.express as px
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.sidebar.header("Let's explore some data")
st.sidebar.markdown("""
Welcome to this Exploratory Data Analysis app.  

This simple app's goal is for a Data Scientist to share findings of the EDA phase of a project
to different project stakeholders, in an interactive fashion.

The data loaded here is stored and governed in a Watson Studio project on IBM Cloud. Learn more [here](https://www.ibm.com/cloud/watson-studio).
""")

st.header("Authenticate and pick a project and dataset")
apikey = st.text_input("Your IBM Cloud API key", type='password', help='Find your API key [here](https://cloud.ibm.com/iam/apikeys)')

auth_ok, headers, error_msg = cpd_helpers.authenticate(apikey)

if not auth_ok:
    st.error("You could not be authenticated. More details below.")
    with st.expander("Expand to see the error message"):
        st.write(error_msg)
else:
    st.success("You are successfully authenticated! Pick a project below.")
    projects, error_msg = cpd_helpers.list_projects(headers)
    _, project_id = st.selectbox("Pick a Watson Studio Project", projects, format_func=lambda x: f"{x[0]} (id: {x[1]}")

if not auth_ok:
    st.write("Please authenticate first.")
else:
    datasets, error_msg = cpd_helpers.list_datasets(headers, project_id)
    _, dataset_id = st.selectbox("Pick a Dataset to analyze", datasets, format_func=lambda x: f"{x[0]} (id: {x[1]}")
    df, error_msg = cpd_helpers.load_dataset(headers, project_id, dataset_id)    

st.header("Dataset preview")
if auth_ok:
    n_rows = st.number_input("Number of rows", min_value=0, max_value=len(df), value=5, help='How many rows to sample and display.')
    sample_strategy = st.radio("How to pick rows", ["Random Sample", "Head"])
    if sample_strategy == "Random Sample":
        st.write(df.sample(int(n_rows)))
    else:
        st.write(df.head(int(n_rows)))
else:
    st.write("Please authenticate first.")

st.header("Visualizations")
if not auth_ok:
    st.write("Please authenticate first.")
else:
    label = st.selectbox("Label column", list(df.columns))
    features = [c for c in df.columns if c != label]
    x_feature = st.selectbox("Feature (X axis)", features)

    st.subheader("Univariate distributions per class")
    st.plotly_chart(px.histogram(df, x=x_feature, color=label, marginal='box'))

    st.subheader("Average default rate per feature bin")
    st.markdown("This plot shows on the x axis a selected feature binned by quantile, \
        and on the y axis the average rate of the label's positive class in each bin. \
        The size of the bins can be selected with the slider below.")

    q_length = st.slider("Quantile size", min_value=0.01, max_value=0.5, step=0.01, value=0.05)
    bins = pd.qcut(df[x_feature], np.arange(0, 1.01, q_length), duplicates='drop')
    rate_per_bin = df.groupby(bins)[label].value_counts(normalize=True)
    fig, ax = plt.subplots()
    rate_per_bin.unstack().plot(kind='bar', stacked=True, ax=ax, rot=45)
    # adjust tick alignments, see https://stackoverflow.com/questions/35262475/controlling-tick-labels-alignment-in-pandas-boxplot-within-subplots
    plt.sca(ax)
    plt.xticks(ha='right')
    ax.set_xlabel(f"Bins of feature {x_feature}")
    ax.set_ylabel(f"Average rate of label {label}")
    st.pyplot(fig)
