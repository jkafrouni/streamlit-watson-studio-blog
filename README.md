# Trust your ML models with Streamlit and IBM Cloud Pak for Data

This repo contains code used for a blog post series covering Streamlit + Cloud Pak for Data integration.  
The goal is to showcase how a Streamlit app can communicate with Watson Studio (on Cloud) to support decision making by various stakeholders in a typical Data Science project.

![predict](https://user-images.githubusercontent.com/18315500/151985079-7b834f4d-e5de-4d2c-85ef-cf0354591783.gif)


## Where to find the blog posts

- [Part 1](https://community.ibm.com/community/user/datascience/blogs/jerome-kafrouni/2022/01/26/trust-your-ml-models-with-streamlit-and-ibm-cloud) covers how to read data from Watson Studio and build your first Streamlit app, to showcase key results of Exploratory Data Analysis
- Part 2 (link published soon) covers how to connect to deployed models and test them from the Streamlit app, as well as Streamlit topics such as adding multiple pages, caching, controlling the UI layout, eetc
- Part 3 (link published soon) covers how to investigate the behavior of these models using SHAP and Partial Dependence Plots, as well as pushing computations to the Cloud using Notbook jobs in Watson Studio.

## How to run the app(s)

Pick a version to run, and navigate to its folder from your terminal. Then, install the `requirements.txt` and start the app with `streamlit run app.py`.

Prerequisites:
- A Watson Studio project, with a dataset and one or multiple deployed ML models
- An API key for IBM Cloud to authenticate to that project

## How to reuse and extend this code

Each part of the blog series is backed by a separate folder from this repo, with increasing complexity. E.g. part 2 has two pages, one of which has the logic previously used in part 1. Depending on your neeeds, you may want to reuse certain portions of either part 1, part 2 or part 3. This choice to organize the repo was made to make going through sample Streamlit and CPD APIs code for the first time easier.
