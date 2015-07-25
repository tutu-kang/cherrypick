from cloudbench.ssh import WaitUntilFinished, WaitForSeconds
from cloudbench.util import Debug, parallel

from cloudbench.apps.hadoop import HADOOP_USER
from cloudbench.cluster.hadoop import HadoopCluster

import re
import time

TIMEOUT=21600

TERASORT_INPUT='/home/{0}/terasort-input'.format(HADOOP_USER)
TERASORT_OUTPUT='/home/{0}/terasort-output'.format(HADOOP_USER)


def terasort_test(vms, env):
    print vms[0].type
    parallel(lambda vm: vm.install('hadoop'), vms)

    cluster = HadoopCluster(vms[0], vms[1:])
    cluster.setup()

    cluster.format_hdfs()
    cluster.restart_dfs()
    cluster.restart_yarn()

    cluster.execute('"hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.1.jar teragen -Dmapred.map.tasks=40 100000000 {0}"'.format(TERASORT_INPUT))
    cluster.execute('"/usr/bin/time -f \'%e\' -o terasort.out  hadoop jar /usr/local/hadoop/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.7.1.jar terasort -Dmapred.reduce.tasks=20 {0} {1} 2>&1"'.format(TERASORT_INPUT, TERASORT_OUTPUT))
    output = cluster.master.script('sudo su - hduser -c "tail -n1 terasort.out"').strip()

    with open(str(time.time())+'-'+cluster.master.type, 'w+') as f:
        f.write(output)

def run(env):
    vms = []
    for i in range(1, 6):
        vms.append(env.vm('vm'+str(i)))

    env.benchmark.executor(vms, terasort_test)
    env.benchmark.executor.run()
    #env.benchmark.executor.stop()

