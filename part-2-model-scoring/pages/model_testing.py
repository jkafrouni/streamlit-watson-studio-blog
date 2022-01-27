import streamlit as st
import cpd_helpers
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from utils import format_tuples


def write_test_predictions(headers, deployment_details, model_details):
    st.markdown("""
    ## Test model predictions
    Pick a row in the table below and click 'Predict' on the right.  
    You can then expand the section below that button to modify the feature
    values and check how your model predictions change.
    """)
    df = st.session_state.get('df', pd.DataFrame())
    gb = GridOptionsBuilder.from_dataframe(df, pre_selected_rows=1)
    gb.configure_selection('single')
    gridOptions = gb.build()

    col1, col2 = st.columns(2)
    with col1:
        grid_response = AgGrid(
            df,
            gridOptions=gridOptions,
            theme='streamlit',
            update_mode=GridUpdateMode.SELECTION_CHANGED,  # important
        )

    with col2:
        with st.form("my_form"):
            proba, previous_proba = st.session_state.get('proba'), st.session_state.get('previous_proba')
            proba_delta = round(proba - previous_proba, 2) if previous_proba is not None else None
            st.metric("Probability", proba, delta=proba_delta)
            st.metric("Predicted Class", st.session_state.get('class_pred'))
            submitted = st.form_submit_button("Predict", help="Click here to get predictions for the row selected on the left or the values entered below.")
            with st.expander("Expand to change feature values"):
                if grid_response['selected_rows']:
                    payload = cpd_helpers.prepare_input_schema(model_details, grid_response['selected_rows'][0])
                    if submitted:
                        (proba, class_pred), error_msg = cpd_helpers.get_deployment_prediction(headers, deployment_details, payload)
                        # we keep track of the previously predicted probability, in order to show delta changes in the st.metric calls above
                        st.session_state['previous_proba'] = st.session_state.get('proba')
                        st.session_state['proba'] = proba
                        st.session_state['class_pred'] = class_pred
                    for k, v in payload.items():
                        if not isinstance(v, str):
                            payload[k] = st.number_input(k, value=v, key=k)
                        else:
                            payload[k] = st.multiselect(k, df[k].unique().tolist(), key=k)
                            # pass
                else:
                    st.write("Select a row on the table on the left to populate this form.")


def write():
    auth_ok, headers = st.session_state.get('auth_ok', False), st.session_state.get('headers')
    st.header("Model testing")
    if not auth_ok:
        st.warning("Not so fast! Head to the first page to authenticate and pick a dataset.")
        return

    spaces, error_msg = cpd_helpers.list_spaces(headers)
    _, space_id = st.selectbox("Pick a Watson Studio Deployment Space", spaces, format_func=format_tuples)

    deployments, error_msg = cpd_helpers.list_deployments(headers, space_id)
    if not deployments:
        st.warning("Oops! Looks like this deployment space is empty.")
        return

    deployment_name, deployment_id = st.selectbox("Pick a Deployed Model or Function",
                                                  deployments, format_func=format_tuples)

    deployment_details, model_details, error_msg = cpd_helpers.get_deployment_details(headers, space_id, deployment_id)
    if error_msg != "":
        st.error("An error happened while retrieving details. More details below.")
        with st.expander("Expand to see the error message"):
            st.write(error_msg)
    else:
        write_test_predictions(headers, deployment_details, model_details)
