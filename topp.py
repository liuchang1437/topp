import time,re
import getopt,sys
import paramiko

def get_param():
    shortargs = 't:n:'
    longargs = ['help']
    opts, args = getopt.getopt(sys.argv[1:],shortargs,longargs)
    interval = 60
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
    temp = ssh.exec_command('ls /proc/fs/lustre/llite')[1].readline().strip()
    #print('cat /proc/fs/lustre/llite/{}/extents_stats_per_process'.format(temp))
    stats_file = ssh.exec_command('cat /proc/fs/lustre/llite/{}/extents_stats_per_process'.format(temp))[1].readlines()
    result = []
    #print(stats_file)
    for line in stats_file:
        item = re.split('\s+', line.strip())
        #print(line)
        result.append(item)
    return result

def show(stats):
    stats_read = []
    stats_write = []
    for pid,rw in stats.items():
        stats_read.append((pid,rw['read_rate']))
        stats_write.append((pid,rw['write_rate']))
    sorted_read = sorted(stats_read,key=lambda x:x[1],reverse=True)
    sorted_write = sorted(stats_write,key=lambda x:x[1],reverse=True)
    print('===========================')
    print('Top reader:')
    print('pid\tbytes')
    for pid,val in sorted_read:
        print('{}\t{} ({}-{})'.format(pid,val,stats[pid]['low_read'],stats[pid]['high_read']))
    print('---------------------------')
    print('Top writer:')
    print('pid\tbytes')
    for pid,val in sorted_write:
        print('{}\t{} ({}-{})'.format(pid,val,stats[pid]['low_write'],stats[pid]['high_write']))
    print('===========================')

def topp():
    interval,node = get_param()
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(node,22,"hpclc", "lc940108")
    while True:
        stats = dict()
        result = get_stats(ssh)
        for index in range(len(result)):
            if result[index][0] == 'PID:':
                pid = result[index][1]
                read_bytes = 0
                write_bytes = 0
                low_read = 0
                low_write = 0
                high_read = 0
                high_write = 0
                offset = 1
                while index+offset<len(result) and result[index+offset][0]!='' and result[index+offset][0] != 'PID:':
                    low = result[index+offset][0]
                    high = result[index+offset][2]
                    low = int(low[:len(low)-1])
                    high = int(high[:len(high)-1])
                    avg = (low+high)/2
                    read_bytes += avg*int(result[index+offset][4])
                    low_read += low*int(result[index+offset][4])
                    high_read += high*int(result[index+offset][4])
                    write_bytes += avg*int(result[index+offset][8])
                    low_write += low*int(result[index+offset][8])
                    high_write += high*int(result[index+offset][8])
                    offset += 1
                if not pid in stats:
                    stats[pid] = dict()
                stats[pid]['read_rate'] = read_bytes
                stats[pid]['write_rate'] = write_bytes
                stats[pid]['low_read'] = low_read
                stats[pid]['high_read'] = high_read
                stats[pid]['low_write'] = low_write
                stats[pid]['high_write'] = high_write
            else:
                continue
        show(stats)
        time.sleep(interval)

if __name__ == '__main__':
    topp()
