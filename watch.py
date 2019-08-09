from resources import  K8S
import time
config_file = 'D:\work\config'
k8s = K8S(config_file=config_file)
time.sleep(10)
print "start...."
k8s.run()