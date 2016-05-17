import time,re
import getopt,sys
import paramiko

stats = dict()
last = dict()


def get_param():
    shortargs = 't:n:'
    longargs = ['help']
    opts, args = getopt.getopt(sys.argv[1:],shortargs,longargs)
    if not len(opts):
        print('Bad command parameters.\nPlease type --help to get more information.')
        exit() 
    for opt,val in opts:
        if opt=='--help':
            print('''Hi, this is topp. There's something may help you.

--help\t get this help message.
-t\t set the interval, 60 secs by default.
-n\t set the nodes to be monitored.''')
            exit()
        elif opt=='-t':
            interval = int(val)
        elif opt=='-n':
            node = val
        else:
            print('Bad command parameters.Please type --help to get more information.')
            exit()
    return (interval,node)

def get_stats(ssh):
    temp = ssh.exec_command('ls /proc/fs/lustre/llite')
    stats_file = ssh.exec_command('cat /proc/fs/lustre/llite/{}/extents_stats_per_second'.format(temp))
    result = []
    for line in stats_file:
        item = re.split('\s+', line.strip())
        result.append(item)
    return result

def show():
    stats_read = []
    stats_write = []
    for pid,rw in stats.items():
        stats_read.append((pid,rw['read_rate']))
        stats_write.append((pid,rw['write_rate']))
    sorted_read = sorted(stats_read,key=lambda x:x[1],reverse=True)
    sorted_write = sorted(stats_write,key=lambda x:x[1],reverse=True)
    print('Top reader:')
    print('pid\tbytes')
    for pid,val in sorted_read:
        print('{}\t{}'.format(pid,val))
    print('===========================')
    print('Top writer:')
    print('pid\tbytes')
    for pid,val in sorted_write:
        print('{}\t{}'.format(pid,val))

def topp():
    interval,node = get_param()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(node,22,"hpclc", "lc940108")
    while  True:
        result = get_stats(ssh)
        for index in range(len(result)):
            if result[index][0] == 'PID:':
                pid = result[index][1]
                read_bytes = 0
                write_bytes = 0
                offset = 1
                while index+offset<len(result) and result[index+offset][0]!='' and result[index+offset][0] != 'PID:':
                    low = result[index+offset][0]
                    high = result[index+offset][2]
                    low = int(low[:len(low)-1])
                    high = int(high[:len(high)-1])
                    avg = (low+high)/2
                    read_bytes += avg*int(result[index+offset][4])
                    write_bytes += avg*int(result[index+offset][8])
                    offset += 1
                if pid in last:
                    stats[pid]['read_rate'] = (read_bytes-last[pid]['read_bytes'])/float(interval)
                    stats[pid]['write_rate'] = (write_bytes-last[pid]['write_bytes'])/float(interval)
                else:
                    last[pid] = dict()
                    stats[pid] = dict()
                    stats[pid]['read_rate'] = 0
                    stats[pid]['write_rate'] = 0
                last[pid]['read_bytes'] = read_bytes
                last[pid]['write_bytes'] = write_bytes            
            else:
                continue
        show()
        time.sleep(interval)

if __name__ == '__main__':
    topp()
