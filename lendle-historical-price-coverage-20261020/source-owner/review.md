# 固定历史价格记录覆盖：候选齐全，USD 单位门尚未通过

本轮仅获取并核对历史价格记录、币种身份及时间覆盖，未做数量乘价格、费用重算、估值、净额、利润或策略运行。实际 model/effort：UNKNOWN。

1. **官方免费入口已核。** 复用上轮 `https://api-docs.defillama.com/llms-free.txt`（完整原件 SHA256 `e8935de2dba00b23e21dfa7bf52dccd1b3c8430587663cb40ba78475729d24e3`）：其标题明确 Free API、no authentication required，并列 GET `/batchHistorical`。本轮从已保存官方首页真实 modulepreload 链接读取 `https://api-docs.defillama.com/assets/api-specifications-Crq_v_wx.js`，2026-10-19 18:38:09–18:38:10 UTC，HTTP200，434211B，SHA256 `bf1e6bc0ba4b58f830f48b0f407af94188c0dc61e70bda4f2767ad0498a93175`。只读文本，未执行 JS。该规范明确币价服务器为 `https://coins.llama.fi`，避免将免费文本的通用 api.llama.fi 基址直接当作币价地址。源未提供可核发布日期；HTTP Date 是读取响应时间，不能当发布日期。
2. **请求与返回结构。** 规范 byte16008 起定义匿名 GET `/batchHistorical?coins=<JSON>`，JSON 为 `{精确链:合约或coingecko:id:[请求Unix时间戳...]}`；返回 `coins → symbol, prices[{timestamp,price,confidence}]`。本次实收也只有 symbol/prices，未返回 decimals、currency、独立 price source 或 requestedTimestamp。规范未给 batchHistorical 的 searchWidth、单向前/后选点保证；chart 仅列 start/end/span/period（byte17272 起）。未使用未文档参数，也未把数组位置冒充请求与返回一一映射证明。
3. **冻结后唯一五批已全部取得。** Root 协议 SHA256 `01946f8f3a98d63060d37fab3993a671b3cc9c2b77d45a97d865c5ca6b7a007e`，固定请求 SHA256 `1e7d741d116397281a1c843a488f6034ecef3ffa2c108c3f98a048a5e32000b1`。全体请求先写 manifest，SHA256 `2d28b3c5624b1d552e306d3f0ffe35d877be53d46b675c2e86d3248df4b9de64`，然后仅发五次 GET，18:39:45–18:39:54 UTC，均 HTTP200、完整 JSON；原体依次 6353/6340/6515/6769/1364B。全部 376 个去重(coin,T−1800)请求对、10 个标识覆盖，含九个精确收款合约及返回 symbol=MNT 的 coingecko:mantle。无重试、补点、换标识/供应商，旧 pilot 未混入。
4. **固定时窗覆盖已齐。** 376 返回价格行归为 227 个唯一(coin,u)，68 组重复均同值，0 冲突、0 非法时间/价格。对固定 119 收款事件和 262 费用事件，均按协议从新返回 pool 选最大 `u∈[T−3600,T]`；全 381 行都有候选，选中点年龄范围 82–2648 秒。实际仅使用 188 个唯一观察，其中 77 个被复用，最多一观察对应 22 事件；不能称 381 个独立市场样本。完整逐事件、逐来源映射在 `fixed381-price-time-mapping.json`，重复来源全部保留。没有以未来点替代主候选，没有冲突后退选、插值、补零或 confidence 过滤。
5. **USD 与兑现边界仍在。** 本次限定官方规范及定向检索尚未取得“该币价字段以 USD 计价”的明确同服务定义，响应本身也没有 currency；因此 price/time 候选覆盖为 381/381，**合格 USD 主 mark 为 0/381，统一美元主账门未通过，本轮未计算美元账**。未证不等于价格并非 USD 或永久不可得。规范 byte10592 起说明价格可能来自 CoinGecko、跨链原币映射、LP/底层赎回比例适配或 DEX 流动性池；所以“请求精确合约标识”不等于独立核实该合约当时可按此价格成交、赎回或变现。返回的观察 timestamp 不晚于交易，也不证明当时已经公开可得；一小时窗口仅为本次会计约定。

公开预算按最保守每条 search_query 各计一次：1 文档 GET + 4 检索 query + 5 批量 GET = 10/10（实际 web 调用三次、含四 query）。全部网络于 18:39:54 UTC 结束。六份 HTTP 原体合计 461552B；搜索结果另按序列化大小保守计入总原体预算。完整资源数和文件哈希见最终回执及 manifest。没有账号、凭证、付费、安装、RPC/EVM、交易、模型或第三方代码执行。

本地一次 Python 拼写语法错误发生于任何语句执行前；查 LOCAL_BLOCKERS 后仅修复自有客户端空格，未重取来源。错误不属于来源拒绝、限流或价格缺失。未修改 Root、方法 Owner、既有账本及原始固定方案。
