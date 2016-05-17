# Topp

## What is Topp?

It's a script to list top N processes running on a node ranked by reading or writing rates.

## 运行机制

每隔一定的时间间隔（默认60s，可以由命令行参数决定），程序读取特定节点的`/proc/fs/lustre/llite/*/extents_stats_per_second`文件，获取进程读写信息。

注意：由于`extents_stats_per_second`文件记录的是进程读写信息的统计状态，如下所示，因此Topp获取的进程读写信息也是一个估值。

```
snapshot_time:         1463449812.379905 (secs.usecs)
                               read       |                write
      extents            calls    % cum%  |          calls    % cum%

PID: 180590
   0K -    4K :              1   50   50  |              0    0    0
   4K -    8K :              1   50  100  |              0    0    0

PID: 180597
   0K -    4K :              1   50   50  |              0    0    0
   4K -    8K :              1   50  100  |              0    0    0

PID: 180616
   0K -    4K :              1   50   50  |              0    0    0
   4K -    8K :              1   50  100  |              0    0    0

PID: 180082
   0K -    4K :              4  100  100  |              0    0    0

PID: 180080
   0K -    4K :              4  100  100  |              0    0    0

PID: 180074
   0K -    4K :              4  100  100  |              0    0    0

PID: 13265
   0K -    4K :              2   66   66  |              0    0    0
   4K -    8K :              0    0   66  |              0    0    0
   8K -   16K :              0    0   66  |              0    0    0
  16K -   32K :              0    0   66  |              0    0    0
  32K -   64K :              0    0   66  |              0    0    0
  64K -  128K :              0    0   66  |              0    0    0
 128K -  256K :              0    0   66  |              0    0    0
 256K -  512K :              0    0   66  |              0    0    0
 512K - 1024K :              1   33  100  |              0    0    0

PID: 180504
   0K -    4K :              2   50   50  |              0    0    0
   4K -    8K :              0    0   50  |              0    0    0
   8K -   16K :              2   50  100  |              0    0    0

PID: 180552
   0K -    4K :              1   50   50  |              0    0    0
   4K -    8K :              1   50  100  |              0    0    0

PID: 180577
   0K -    4K :              1   50   50  |              0    0    0
   4K -    8K :              1   50  100  |              0    0    0

```

## 命令行参数

```
-- help 打印帮助信息
-t 设定时间间隔，默认60s
-n 设定要获取的节点名称（必须）
```

## 后续

获得读写速率最高的进程pid后，管理员账户可以根据slurm提供的信息获得该进程所属的应用名称及账户名称。