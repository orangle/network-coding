# python NAT 穿孔测试实验

之前只是知道大概流程，原来还有标准协议

- https://github.com/laike9m/PyPunchP2P
- https://github.com/jtriley/pystun
- https://github.com/sporsh/jostedal
- [RFC 6970 UPnP](https://tools.ietf.org/html/rfc6970)
- [RFC 5389 STUN](https://tools.ietf.org/html/rfc5389)
- [RFC 5766 TURN](https://tools.ietf.org/html/rfc5766)
- [UPnP基本原理以及在NAT中的应用](http://www.h3c.com.cn/MiniSite/Technology_Circle/Net_Reptile/The_Five/Home/Catalog/201206/747039_97665_0.htm)
- [TURN and STUN Server](https://github.com/coturn/coturn)

* 使用udp做信令系统？

因为是用NAT可以保持部分时间的窗口有效，所以用心跳维持 UDP 链接，然后服务端做信令下发，构成双向信令

* 穿孔的情况比较多，有的是无法直连，有的只能udp，有的需要tcp来做流量中继，有的需要udp中继。


### UPnP

以下是摘抄

UPnP协议结构最底层的TCP/IP协议是UPnP协议结构的基础。IP层用于数据的发送与接收。对于需要可靠传送的信息，使用TCP进行传送，反之则使用UDP。UPnP对网络的底层没有要求，可以是以太网、WIFI、IEEE1394等等，只需支持IP协议即可。

构建在TCP/IP协议之上的是HTTP协议及其变种，这一部分是UPnP的核心，所有UPnP消息都被封装在HTTP协议及其变种中。HTTP协议的变种是HTTPU和HTTPMU，这些协议的格式沿袭了HTTP协议，只不过与HTTP不同的是他们通过UDP而非TCP来承载的，并且可用于组播进行通信。

- SSDP  简单服务发现协议（Simple Service Discovery Protocol：SSDP
- SOAP  简单对象访问协议（Simple Object Access Protocol：SOAP）
- GENA  通用事件通知架构（Generic Event Notification Architecture：GENA）

如果用户是通过NAT接入Internet的，同时需要使用BC、电骡eMule等P2P这样的软件，这时UPnP功能就会带来很大的便利。利用UPnP能自动的把BC、电骡eMule等侦听的端口号映射到公网上，以便公网上的用户也能对NAT私网侧发起连接。

必须条件

- NAT网关设备必须支持UPnP功能
- 操作系统必须支持UPnP功能；我们常见的Windows XP是支持UPnP的
- 应用软件必须支持UPnP功能；比如BC、电骡eMule、MSN软件都是支持的；

局域网测试发现很多 SSDP的协议包, 基于udp协议，发送的协议是http协议

设备发现有2种模式
- 主动告知 设备加入网络之后，向控制点告知他提供的服务 (NOTIFY请求) 
    + 发送自己的uuid, Location信息给其他设备，cache时间
    + 响应 200OK
- 利用查询发现   (M-SEARCH请求) 抓包看到chrome有不少这种请求



抓包测试 
- https://github.com/flyte/upnpclient
- [案例分析Upnp协议实现自动端口映射](http://read.pudn.com/downloads148/doc/639770/%E6%A1%88%E4%BE%8B%E5%88%86%E6%9E%90Upnp%E5%8D%8F%E8%AE%AE%E5%AE%9E%E7%8E%B0%E8%87%AA%E5%8A%A8%E7%AB%AF%E5%8F%A3%E6%98%A0%E5%B0%84.pdf)

Client 首先通过 SSDP协议发现设备A，然后通过返回的信息得到  `设备类型`，`UUID`, `Location`信息，然后就是通过TCP的SOAP协议和设备A交互，获取设备描述，然后发送控制指令，获取外网地址，然后发送自动mapping port功能，这样就得到了公网的IP和端口，发送心跳就可以保持。









