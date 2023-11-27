FROM --platform=linux/x86_64 amazon/aws-lambda-python:3.9

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

COPY visualize_network.py ${LAMBDA_TASK_ROOT}
COPY config ${LAMBDA_TASK_ROOT}/config

CMD [ "visualize_network.lambda_handler" ]