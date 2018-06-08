网络编程笔记一
============


初学者常见的错误
* 网络IO和业务逻辑混杂在一起
* TCP 不可靠
* 消息的边界问题，tcp无法知道消息完整性
* 直接发送结构体
* tcp 自连接，同一个端口
* 非阻塞编程比较多坑

测试网络速度，本机走的是本地网卡

```
#A
# nc -vvv -l -p 10008 > /dev/null 

#B
# dd if=/dev/zero bs=1M count=1000 | nc localhost 10008
记录了1000+0 的读入
记录了1000+0 的写出
1048576000字节(1.0 GB)已复制，5.99562 秒，175 MB/秒

#A 使用pv工具
# nc  -vvv -l 10000|pv -W > /dev/null
Connection from 127.0.0.1 port 10000 [tcp/ndmp] accepted
0.977GB 0:00:13 [73.8MB/s] [                                  <=>
```

cpu等也会影响带宽，系统调用影响蛮大

### 案例ttcp

简单的交互流程

```
Client                       Server
    ------- (length, num) ------>
 1  ------- (lenth, payload) --->
    <------- ack (length) ------
    ...
 num ------- (lenth, payload) --->
    <------- ack (lenth) ----  close
```

注意这里的第一个请求没有ack

测试结论，发送包越大吞吐越高


### tcp 阻塞实验

第7讲中，说明了阻塞socket一个经典的问题，之前么有弄懂阻塞IO有什么危害？

例如 client 使用了阻塞IO，send数据没有完成之前，是无法进行read的，大文件收发同时进行时候可能会被阻塞僵死。

tcp 缓冲，内核参数对收发有影响。

### tcp 自连接

第8讲中，说了一个 linux下 tcp 自连接的问题

```
# sysctl -A|grep port_range
net.ipv4.ip_local_port_range = 1024	65000
```

端口的范围


### 其他

* 测试数据不能太少，tcp慢启动会在测试开始的时候会有影响





