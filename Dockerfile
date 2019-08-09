FROM python:2.7
ADD . /app/
RUN pip install kubernetes
ENV NAMESPACES=default SELECT_LABLE=app KUBE_CONF_PATH="$HOME/.kube/config"  IN_CLUSTER=""
CMD ["python","/app/watch.py"]