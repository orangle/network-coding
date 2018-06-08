网络编程笔记二
============

### UDP vs TCP

UDP 和 TCP 的不同？
* UDP 是无连接，不可靠的，数据报协议
	- IP + port (+weak checksum)
* TCP 面向连接，可靠的，字节流协议
* 并发模型：怎样管理并发 clients
	- TCP 每个client一个 socket fd，线程不安全
	- UDP 所有clients共享一个 socket fd, 线程安全

### simple netcat

netcat 常用的功能
* nc < /dev/zero == 生成字符
* nc > /dev/null == 网络黑洞
* dd /dev/zero |nc == 用来做带宽测试
* nc < file , nc > file == 用来做简单的scp

#### TCP 难度阶梯

* 销毁连接 > 建立连接
* 客户端建立连接 > 服务建立连接
* 发送数据 > 接受数据难度

### TCP 坑

* 为什么我的TCP不可靠呢？
	- send 所有数据就 close, 但是最后几个字节丢了
* 错误的：send() close()
	- 当 input buffer 有数据的时候，close() 会引起一个 RST，过早的关闭连接
	- TL, DR: 不要使用 LINGER (???没看懂)
* 正确的 sender: send() + shutdown(wr) + read -> 0 + close()
* 正确的 recever: read() -> 0 + if nothing more to send + close()
* 通过正确的应用层协议来保证边界

### 三部曲

* SO_RESUSEADDR
* Ignore SIGPIPE
* TCP_NODELAY




