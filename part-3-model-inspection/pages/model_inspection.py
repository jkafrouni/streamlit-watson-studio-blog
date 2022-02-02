import streamlit as st
import matplotlib.pyplot as plt
import shap

import numpy as np

import cpd_helpers
from utils import format_tuples, make_basic_roc_curve, make_advanced_roc_curve, format_autoai_results


def write_shap_job_select(headers, model_details):
    project_id, dataset_id = st.session_state.get('project_id'), st.session_state.get('dataset_id')
    if (project_id is None) or (dataset_id is None):
        st.warning("Oops! Looks like you have not selected a project or dataset on the first page yet.")
        return

    jobs, error_msg = cpd_helpers.list_jobs(headers, project_id)
    if jobs:
        _, job_id = st.selectbox("Pick a Notebook Job", jobs, format_func=format_tuples)
        n_env_vars = st.number_input("Number of environment variables", min_value=0, value=1, step=1)
        col1, col2, _ = st.columns([2, 2, 6])
        env_vars = dict()
        for i in range(int(n_env_vars)):
            key = col1.text_input("", placeholder=f"KEY{i+1}", key=f"key_{i}")
            value = col2.text_input("", placeholder=f"VALUE{i+1}", key=f"value_{i}")
            env_vars[key] = value
        env_vars['MODEL_ID'] = model_details['metadata']['id']
        st.button("Trigger job", on_click=cpd_helpers.trigger_job, args=(headers, project_id, job_id, env_vars))
    else:
        st.warning("Oops! Looks like there are no jobs in your project yet.")


def write_shap_plots(headers, model_details):
    st.markdown("""
    ### Inspect your model's SHAP values
    """)
    precomputed_shap = model_details.get('entity').get('custom', dict()).get('shap')
    if not precomputed_shap:
        st.warning("Looks like you haven't precomputed SHAP values yet!\
            You can compute them using the section below")
        with st.expander("Expand to compute SHAP values in Watson Studio"):
            write_shap_job_select(headers, model_details)
            return

    exp = shap.Explanation(np.array(precomputed_shap['values']),
                           base_values=precomputed_shap['expected_value'],
                           feature_names=precomputed_shap['feature_names'],
                           data=np.array(precomputed_shap['data'])
                           )
    fig, _ = plt.subplots(figsize=(10, 10))
    shap.plots.beeswarm(exp, show=False)
    st.write(fig)


def write_other_available_results(headers, model_details):
    st.markdown("""
    ### Additional model information (AutoAI only)
    If your model was trained in AutoAI, additional information can be retrieved
    from its metadata and displayed below.
    """
    )
    metrics = model_details['entity'].get('metrics')
    if metrics is None:
        st.info("Select a model created with AutoAI to display additional information.")
        return

    st.markdown("#### Training metrics")
    st.write(format_autoai_results(metrics[0]['ml_metrics']))

    st.markdown("#### ROC curve")
    roc = metrics[0]['context']['binary_classification']['roc_curve'][1]

    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(make_basic_roc_curve(roc['fpr'], roc['tpr']))

    with col2:
        st.plotly_chart(make_advanced_roc_curve(roc['fpr'], roc['tpr'], roc['thresholds']))


def write():
    auth_ok, headers = st.session_state.get('auth_ok', False), st.session_state.get('headers')
    st.header("Model inspection")
    if not auth_ok:
        st.warning("Not so fast! Head to the first page to authenticate and pick a dataset.")
        return

    spaces, error_msg = cpd_helpers.list_spaces(headers)
    _, space_id = st.selectbox("Pick a Watson Studio Deployment Space", spaces, format_func=format_tuples)

    deployments, error_msg = cpd_helpers.list_deployments(headers, space_id)
    if not deployments:
        st.warning("Oops! Looks like this deployment space is empty.")
        return

    _, deployment_id = st.selectbox("Pick a Deployed Model or Function",
                                    deployments, format_func=format_tuples)

    deployment_details, model_details, error_msg = cpd_helpers.get_deployment_details(headers, space_id, deployment_id)
    if error_msg != "":
        st.error("An error happened while retrieving details. More details below.")
        with st.expander("Expand to see the error message"):
            st.write(error_msg)
    else:
        write_shap_plots(headers, model_details)
        write_other_available_results(headers, model_details)
