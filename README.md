#功能说明

**实现confmaps 更新后 ,应引用了该configmap的deployment 实现滚动升级**

#环境变量说明
##IN_CLUSTER
是否在集群内部运行，如果没有设定，则默认为不在集群内运行
##KUBE_CONF_PATH
如果IN_CLUSTER=true的话，改变量可以不用设置，如果不在默认$HOME/.kube/config 
##SELECT_LABLE
该变量需要在configmap ，deployment 设置相同的 标签，SELECT_LABLE 为搜索标签的key
****
`可以设定为 app: ops-h5 或者configmaps: ops-h5`
```
apiVersion: v1
data:
  k: ppipoo
  e: oohjdhfhe
kind: ConfigMap
metadata:
  labels:
    app: ops-h5
    configmaps: ops-h5
  name: ops-h5
  namespace: ph-dev
```
```
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  annotations:
    deployment.kubernetes.io/revision: "29"
  labels:
    app: ops-h5
    configmaps: ops-h5
    version: v1
  name: ops-h5
  namespace: ph-dev
spec:
  replicas: 1
   ....
```
##NAMESPACES
这个参数如果在集群内部则不需要设置该参数，默认取部署所在的集群
也可以指定 此值，但是configmaps 和deployment 必须在同一namespace


