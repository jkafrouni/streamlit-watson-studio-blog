# based on https://www.section.io/engineering-education/how-to-deploy-streamlit-app-with-docker/#dockerizing-the-streamlit-app
FROM python:3.8
WORKDIR /part-3-model-inspection

COPY part-3-model-inspection/requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./part-3-model-inspection .

ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]
