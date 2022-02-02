# Trust your ML models with Streamlit and IBM Cloud Pak for Data

This repo contains code used for a blog post series covering Streamlit + Cloud Pak for Data integration.  
The goal is to showcase how a Streamlit app can communicate with Watson Studio (on Cloud) to support decision making by various stakeholders in a typical Data Science project.

![predict](https://user-images.githubusercontent.com/18315500/151985079-7b834f4d-e5de-4d2c-85ef-cf0354591783.gif)


## Where to find the blog posts

- [Part 1](https://community.ibm.com/community/user/datascience/blogs/jerome-kafrouni/2022/01/26/trust-your-ml-models-with-streamlit-and-ibm-cloud) covers how to read data from Watson Studio and build your first Streamlit app, to showcase key results of Exploratory Data Analysis
- Part 2 (link published soon) covers how to connect to deployed models and test them from the Streamlit app, as well as Streamlit topics such as adding multiple pages, caching, controlling the UI layout, eetc
- Part 3 (link published soon) covers how to investigate the behavior of these models using SHAP and Partial Dependence Plots, as well as pushing computations to the Cloud using Notbook jobs in Watson Studio.

## How to run the app(s) locally

Pick a version to run, and navigate to its folder from your terminal. Then, install the `requirements.txt` and start the app with `streamlit run app.py`.

Prerequisites:
- A Watson Studio project, with a dataset and one or multiple deployed ML models
- An API key for IBM Cloud to authenticate to that project

## How to reuse and extend this code

Each part of the blog series is backed by a separate folder from this repo, with increasing complexity. E.g. part 2 has two pages, one of which has the logic previously used in part 1. Depending on your neeeds, you may want to reuse certain portions of either part 1, part 2 or part 3. This choice to organize the repo was made to make going through sample Streamlit and CPD APIs code for the first time easier.

---

## How to host the app on Streamlit Cloud

Visit [Deploy an app](https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app) in the Streamlit docs to learn more.

## How to host the app on IBM Cloud Code Engine

If you want to host the app in IBM Cloud instead, Code Engine is an IBM service that offers serverless app hosting capabilities. What that means is that you can build a Docker image and host it as on IBM Cloud with a few CLI commands, without worrying about provisioning virtual machines, or any networking considerations. You can then scale the app up or down, update it in place, etc. 

### Step 0 - Prerequisites

In order to deploy this application on Code Engine you will need:
1. The [Docker CLI](https://docs.docker.com/get-docker/) installed locally
2. The [IBM Cloud CLI](https://cloud.ibm.com/docs/cli?topic=cli-install-ibmcloud-cli) installed locally

### Step 1 - Build and test a docker image locally
You can use the `Dockerfile` included in this repository to build a docker image. For example, you may call the image
`model-inspection`. Once the image is built, test it locally using `docker run` and don't forget to expose port 8501 which is the default port used by streamlit.

```
>>> docker build -t model-inspection .
>>> docker run -p 8501:8501 model-inspection
```

The application will be available on `http://localhost:8501/`.

### Step 2 - Log in to the IBM Cloud CLI
Log in to your IBM Cloud account using the IBM Cloud CLI. A "getting started" guide is available at https://cloud.ibm.com/docs/cli?topic=cli-getting-started.
For example you can log in using an api key inline, and set the resource group to `default`, with:
```
ibmcloud login --apikey <replace-me> -g default
```

You will need the following plugins:
```
ibmcloud plugin install code-engine
ibmcloud plugin install container-registry
```

### Step 3 - Prepare a Container Registry namespace
We will be pushing the image created in step 1) into a container registry under your IBM Cloud account.  
Your container registry is organized in different namespaces. If you don't have a namespace ready, log in to CR (container registry) and create a namespace
by running the following:
```
ibmcloud cr login
ibmcloud cr namespace-add my-namespace
```

### Step 4 - Push your image
Now that you have a place to store the image from step 1, push it to that registry with the following where you replace `my-namespace` in `us.icr.io/my-namespace/model-inspection` with the name you used in the command above.
```
docker tag model-inspection:latest us.icr.io/my-namespace/model-inspection
docker push us.icr.io/my-namespace/model-inspection
```

If you get an error when running the code above you might want to double check that you are logged into CR by running `ibmcloud cr login` again.

### Step 4 - Create a Code Engine project
Code Engine organizes applications and other artifacts in projects. If you don't have a project ready, create one by running the following:
```
ibmcloud ce project create --name my-first-project
```
If you already had a CE project defined, use:
```
ibmcloud ce project select -n my-first-project
```

### Step 5 - Set up access to Container Registry from Code Engine
**Read carefully:** To make sure that your Code Engine project can pull and push from/to your Container Registry, you need to set a CE parameter called registry which represents the connection to your account's registry. Note that when creating applications through the UI, Code Engine can automatically connect to the registry under the same account, but when using the CLI this step is **mandatory**.

In the code below, keep the `--username` value as `iamapikey` and replace `<your-apikey>` with the API key of an account that has access to both the Container Registry namespace created in Step 3 and the Code Engine project from Step 4.
```
ibmcloud ce registry create --name my-container-registry --server us.icr.io --username iamapikey --password <your-apikey>
```

### Step 6 - Create the Code Engine application
As a summary we now have:
- a container registry namespace defined in step 3 which contains the image of our application pushed in step 4
- a Code Engine project defined in step 5, which can access the container registry thanks to step 5, and is ready to host your application

The last step is now to actually create the application with the following command. Notes on some arguments used:
- `--port`: It is **very important** to make sure that `--port` is passed and set to the port used by streamlit, 8501.
- `--request-timeout`: Streamlit is stateful and maintains a [session state variable](https://docs.streamlit.io/library/api-reference/session-state) for each user. This is done by opening a websocket connection between the end user's browser
  and streamlit running remotely. When the connection dies, the session is reset. In particular **we use this session state as a way to check if the user is authenticated**. In CE, connections time out after a given amount of time. We pass
  the value of 600 seconds (10 minutes), which is the maximum value possible in Code Engine as of Nov 2021.

```
>>> ibmcloud ce application create \                                                
--name model-inspection \
--image us.icr.io/my-namespace/model-inspection \
--registry-secret my-container-registry \
--port 8501 \
--request-timeout 600
```

There are many more configuration parameters available. Use `ibmcloud ce application create --help` for a complete list. In particular, you can define scaling policies to scale up or down when needed.

### Step 7 - Monitoring, update, and deletion
If the application was created successfully, the output of the `ibmcloud ce application create` command will contain the url for your application.  
For example https://model-isnpection.some-unique-id.us-south.codeengine.appdomain.cloud/.  

You are able to inspect logs by running:
```
ibmcloud ce application logs -n model-inspection -f     
```

You can make updates to the application without shutting it down or having to change the url. The command to make updates to an application is
`ibmcloud ce application update` and takes similar arguments as `ibmcloud ce application create`.

- Changes to code: Simply update your image by re-running steps 1 and 4. Then, run `ibmcloud ce application update -n model-inspection
- Changes to configuration: If you need to change an environment variable for example, run `ibmcloud ce application update -n model-inspection -e SOME_ENV_VAR_KEY=<my-new-var>`
