- YBMEX 提供 WebSocket Pub/Sub API ， 您可以订阅交易数据的实时更改。

  - 连接
    - 所有指令
    - 订阅
    - 验证
      - API 密钥
  - 心跳
  - 响应数据格式

  ### 连接

  将您的 WebSocket 客户端连接到 wss://www.ybmex.com/realtime。

  通过发送 "help"，你可以基本了解如何使用我们的 WebSocket API 。

  #### 所有指令

  基本的命令发送的格式︰

  ```
  {"op": "<command>", "args": ["arg1", "arg2", "arg3"]}
  ```

  在某些命令上，参数数组是可选的。 如果您只发送一个参数，则数组不是必需的。

  - 订阅：
    - subscribe（订阅）
    - unsubscribe（取消订阅）
  - 身份验证（账户数据）
  - 心跳
    - Ping

  > WebSocket 不支持新增和取消委托。 此功能请使用 REST API。 在使用时保持 HTTP 连接，请求/响应的往返时间将与 WebSocket 完全相同。

  #### 订阅

  YBMEX 允许订阅实时数据。 一旦连接成功，该访问方方式没有频率限制，它是获取最新数据的最好方法。

  要订阅主题，请发送逗号分隔的主题列表。例如︰ 例如：

  wss://www.ybmex.com/realtime?subscribe=instrument:XBTUSD,order:XBTUSD,orderBookL2:XBTUSD,trade:XBTUSD,liquidation:XBTUSD

  如果您已连接，并且想要订阅一个新主题，请发送以下格式的请求︰

  {"op": "subscribe", "args": [<SubscriptionTopic>]}

  通过发送订阅主题数组，您可以一次订阅多个主题。

  下面的订阅主题是无需身份验证：

  ```
  "orderBookL2_25", // 前25层的Level2委托列表 
  "orderBookL2",    // 完整的level2委托列表 
  "orderBook10",    // 前10层的委托列表，用传统的完整委托列表推送
  "quote",          // 最高层的委托列表
  "trade",          // 实时交易，对应UI近期交易列表 
  "instrument",     // 产品更新，包括交易量以及报价 
  "liquidation",    // 进入委托列表的强平委托
  ```

  下列主题要求进行身份验证︰

  ```
  "margin",         // 你账户的余额和保证金要求的更新 
  "positon",        // 你仓位的更新 
  "execution",      // 获取您账户所有的原始执行 
  "order",          // 资金提存更新 
  ```

  如果您想获得实时委托列表数据，建议您使用 orderBookL2_25 订阅。 orderBook10 在任何数据变动时都推送完整的 10 个深度列表，这意味着更多的数据量。 orderBookL2 推送完整的 L2 委托列表，但有效载荷可以变得非常大。 orderbookL2_25 提供完整 L2 委托列表的子集，但受到限制。 如果对延时有较高要求，请使用 orderBookL2。 对于大家可能提出的疑问，在 orderBookL2_25 或 orderBookL2 中的 id 字段是是唯一的，可以被用于 update 和 delete 操作。

  示例数据：

  ```
  > {"op": "subscribe", "args": ["orderBookL2_25:XBTUSD"]}
    < {"success":true,"subscribe":"orderBookL2_25:XBTUSD","request":{"op":"subscribe","args":["orderBookL2_25:XBTUSD"]}}
    < { "table":"orderBookL2_25", "keys":["symbol","id","side"], "types":{"id":"long","price":"float","side":"symbol","size":"long","symbol":"symbol"} "foreignKeys":{"side":"side","symbol":"instrument"}, "attributes":{"id":"sorted","symbol":"grouped"}, "action":"partial", "data":[
          {"symbol":"XBTUSD","id":17999992000,"side":"Sell","size":100,"price":80},
          {"symbol":"XBTUSD","id":17999993000,"side":"Sell","size":20,"price":70},
          {"symbol":"XBTUSD","id":17999994000,"side":"Sell","size":10,"price":60},
          {"symbol":"XBTUSD","id":17999995000,"side":"Buy","size":10,"price":50},
          {"symbol":"XBTUSD","id":17999996000,"side":"Buy","size":20,"price":40},
          {"symbol":"XBTUSD","id":17999997000,"side":"Buy","size":100,"price":30}
        ]
      }
    < { "table":"orderBookL2_25", "action":"update", "data":[
          {"symbol":"XBTUSD","id":17999995000,"side":"Buy","size":5}
        ]
      }
    < { "table":"orderBookL2_25", "action":"delete", "data":[
          {"symbol":"XBTUSD","id":17999995000,"side":"Buy"}
        ]
      }
    < { "table":"orderBookL2_25", "action":"insert", "data":[
          {"symbol":"XBTUSD","id":17999995500,"side":"Buy","size":10,"price":45},
        ]
      }
  ```

  订阅后，您将收到现有数据的镜像，以便您可以开始使用。 这通过partial实现。

  > 您可能会在partial通过之前收到其它消息。 在这种情况下，请除去收到的消息，直到收到partial 。

  对于数据回应的一些注意事项：

  - 订阅确认后，您将收到一条消息，其中包含 “action”：“partial” 。 该信息是您要求数据的当前镜像，在这之后，您可以基于它使用增量变化。
    - 如果您在 partial 消息之前收到任何其他消息，请忽略它们。
  - partial 还包含一些表格信息，如 keys ，types 和 foreignKeys 。 根据您的应用程序，这些数据可能会很有用。
    - 在keys中的列总是返回一个插入 ，删除 ，或更新 。 使用它们查找要在存储中修改哪些项目。

  您可以使用'取消订阅'操作。 格式与 "订阅" 相同。

  #### 验证

  许多数据流是公开的。 如果您希望订阅用户私有数据流，则必须先进行身份验证。 请注意，无效的身份验证将关闭连接。

  ##### API 密钥

  YBMEX API 的使用需要 API 密钥。

  永久的 API 密钥可以被锁定到某个 IP 地址的范围，撤消该密钥并不影响您的主要身份验证。他们也不需要更新。 他们也不需要续约。

  若要使用 API 密钥身份验证，您必须生成一个 API 密钥。

  若要使用 WebSocket API 密钥，您可以︰

  ```
  * 签署最初的申请请求，与签署 REST 调用类似（即利用 `api-*` 标头），
  或者
  * 在连接建立后，发送 `"authKeyExpires"`。
  ```

  无论哪种方式，请使用签署 GET /realtime 的签名。 

  ```
  //签名是十六进制的 hex(HMAC_SHA256(secret, 'GET/realtime' + expires)) // expires 必须是一个数字，而不是一个字符串。 {"op": "authKeyExpires", "args": ["<APIKey>", <expires>, "<signature>"]}
  ```

  ### 心跳

  某些 WebSocket 代码库比其它库能更好地检测连接断开。 如果你的 WebSocket 库支持 ping/pong，你可在任何时间发送 ping ，服务器就会返回pong。

  如果你担心你的连接被默默地终止，我们推荐你采用以下流程：

  - 在接收到每条消息后，设置一个30秒钟的定时器。
  - 如果在定时器触发收到任何新消息，则重置定时器。
  - 如果定时器被触发了（意味着30秒内没有收到新消息），发送一个 ping 数据帧（如果支持的话），或者发送字符串 'ping'。
  - 期待一个原始的pong框架或文字字符串'pong'作为回应。 如果在30秒内未收到，请发出错误或重新连接。

  #### 响应数据格式

  WebSocket 的响应可能有以下三种类型：

  *Success*:（成功订阅一个主题后发出）

  ```
  {"subscribe": subscriptionName, "success": true}
  ```

  *Error*: （格式错误的请求或试图请求锁定的资源时发出）

  ```
  {"error": errorMessage}
  ```

  *数据*：（当数据可用或被请求时发出）

  > 此定义遵循FlowType和TypeScript中使用的输入约定。 后缀为？的字段并不总是存在。 

  ```
  { 
  	// 数据表名 / 订阅主题 
  	// 可以是 "trade"，"order"，"instrument" 等等 
  	
  	"table": string, // 消息类型。 类型: 
  	// 'partial': 这是数据表镜像，将完全替换你的数据。 
  	// 'update': 单行更新 
  	// 'insert': 插入一个新行 
  	// 'delete': 删除一行 
  	"action": 'partial' | 'update' | 'insert' | 'delete', 
  	
  	// 这里发出一组数据行。 他们是在结构上与从 REST API 返回的数据相同。 
  	"data": Object[], 
  	
  	// 
  	// 以下字段定义了数据表，仅在`partial`中发送 
  	// 
  	
  	// 每个数据对象的特征名称是唯一的 
  	// 如果提供多个，则采用复合键名 (key)。 
  	// 使用这些 key 的名称来唯一地标识数据列。  
  	// 你接收的左右数据均包含 key 列。 
  	
  	"keys"?: string[], 
  	// 这里列出了与其他数据表的数据键之间的关系。 
  	// 例如，`quote`的外部键是 {"symbol": "instrument"} 
  	"foreignKeys"?: {[key: string]: string}, 
  	
  	// 这里列举了数据表的数据类型。 可能的类型为： 
  	// "symbol" - 在大多数语言中类似于 "string" 
  	// "guid" 
  	// "timestamp" 
  	// "timespan" 
  	// "float" 
  	// "long" 
  	// "integer" 
  	// "boolean" 
  	"types"?: {[key: string]: string}, 
  	
  	// 如果存在对于同一数据表的多个订阅，请使用 `filter` 来指明不同的订阅 
  	// 所包含的数据，这是因为 `table` 属性并不包括某一订阅的合约标记。 
  	"filter"?: {account?: number, symbol?: string}, 
  	
  	// 这些是我们内部的特征名称，用来代表这些数据是如何被排序已经组合的。 
  	"attributes"?: {[key: string]: string},
  }
  ```
