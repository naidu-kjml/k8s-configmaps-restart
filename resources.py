# -*- coding: utf-8 -*-
import os
import  datetime
from kubernetes import client, watch ,config
from kubernetes.client.rest import ApiException
config_file = 'D:\work\config'

class K8S(object):

    def __init__(self,config_file=None):

        in_cluster = True if os.environ.get("IN_CLUSTER") else False
        if in_cluster:
            config.load_incluster_config()
        else:
            config_file = os.environ.get('KUBE_CONF_PATH') if os.environ.get('KUBE_CONF_PATH') else config_file
            config.load_kube_config(config_file=config_file)
        self.in_cluster = in_cluster
        self.select_lable = 'configmaps' if not os.environ.get('SELECT_LABLE') else os.environ.get('SELECT_LABLE')

    def get_namespaces(self):
        if self.in_cluster:
            namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()
        else:
            namespace = os.environ.get("NAMESPACES") if os.environ.get("NAMESPACES") else "default"
        return namespace

    def _get_lable_value(self,lables):
        if lables is None:
            lable_value = ""
        elif self.select_lable in lables.keys():
            lable_value = lables.get(self.select_lable,'')
        else:
            lable_value = ""
        print "%s selecter_lable: %s=%s" % (datetime.datetime.now(),self.select_lable,lable_value)
        return  lable_value

    def _get_deployment_name(self,lable):
        cli = client.AppsV1Api()
        label_selector = "%s=%s" % (self.select_lable, lable)
        deployment_objects = cli.list_namespaced_deployment(namespace=self.get_namespaces(),
                                                            label_selector=label_selector ,
                                                            watch=False)
        names = []
        for obj in deployment_objects.items:
            names.append(obj.metadata.name)
        return names

    def _patch_deployment(self,name):
        update_time = datetime.datetime.now()
        body = {"spec":{"template":{"metadata":{"annotations":{"configmapsupdate":update_time}}}}}
        cli = client.ExtensionsV1beta1Api()
        try:
            response = cli.patch_namespaced_deployment(name,namespace=self.get_namespaces(),body=body)
            print "%s patch_deployment %s" % (datetime.datetime.now(),name)
        except ApiException  as e:
            print("Exception when calling ExtensionsV1beta1Api->patch_namespaced_deployment: %s\n" % e)
    def watch_config_maps(self):
        v1 = client.CoreV1Api()
        w = watch.Watch()
        stream = w.stream(v1.list_namespaced_config_map,namespace=self.get_namespaces())

        for event in stream:
            eventType = event.get('type')
            configmapsObject = event.get('object')
            print "%s configMaps %s %s" % (datetime.datetime.now(), configmapsObject.metadata.name,eventType)
            if eventType == "MODIFIED":
                lables = configmapsObject.metadata.labels
                lable_value = self._get_lable_value(lables)
                if lable_value:
                    deployments_name = self._get_deployment_name(lable_value)
                    for deployment in deployments_name:
                        self._patch_deployment(deployment)

    def run(self):
        while True:
            try:
                self.watch_config_maps()
            except ApiException as e:
                if e.status != 500:
                    print("ApiException when calling kubernetes: %s\n" % e)
                else:
                    raise
            except Exception as e:
                print("Received unknown exception: %s\n" % e)

if __name__ == "__main__":
    k8s = K8S(config_file=config_file)
    k8s.run()