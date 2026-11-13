# Lendle现有原件：账字段与真实入口盘点

**已有可追账的E顶层索引、个案原始代币流与长精度单笔费用；尚缺全体交易精确费用和指定期初末的完整资产负债状态。** 这是本地原件覆盖盘点，不是“公开全账不存在”或策略盈亏结论。仅按指定两个证据单元读取，零网络、零金额汇总/相减/换算；没有重做部署字节码解码。

## 最小原始链接清单

均来自实际HTML href，原值/文件/行号见`minimal-original-links.json`，没有从JS拼接或换地址猜端点。

| 入口 | 实际URL与来源 | 已证/未知 |
|---|---|---|
| E CSV | [CSV Export](https://mantlescan.xyz/exportData?type=address&a=0x57d8718f0d24db1f3f6445337c8a0c24948d77c2)，E address.source.html L2649；history-page1 L1406 | href真实；Root本轮另报普通GET403，已停；本Owner未访问，不保证可下载 |
| E历史余额 | [Check Previous Balance](https://mantlescan.xyz/balancecheck-tool?a=0x57d8718f0d24db1f3f6445337c8a0c24948d77c2)，E页L1101 | 入口文字真实；Root另报GET403，不能据href宣称已取得历史余额 |
| X内部交易 | [Advanced View](https://mantlescan.xyz/address/0x5483e9260d84b16ac5a32f2CEB333C762dB74718/advanced#internaltx)，X页L1686 | 地址专属真实链接；内容、登录、分页/保留和调用树完整性UNKNOWN |
| E的mETH持有人页 | [mETH / E](https://mantlescan.xyz/token/0xcda86a272531e8640cd7f1a92c01839911b90bb0?a=0x57d8718f0d24db1f3f6445337c8a0c24948d77c2)，E页L1174 | 当前持仓中实际链接；尚未认证为全历史转账/历史余额数据入口 |
| ERC20转账/内部交易总入口 | [tokentxns](https://mantlescan.xyz/tokentxns) / [txsInternal](https://mantlescan.xyz/txsInternal)，两地址页L652/L577 | 仅全站导航，不是已过滤的E/X账；未补造?a=参数 |

X页也确有CSV及Check Previous Balance的专属href（L2497/L1101），完整保存于JSON；**它们仅作库存，不作为E入口403后的替换访问方案**。E/X的ERC20 tab实际href为`javascript:;`（E L1289、X L1239）；X普通internal tab同样为JS标签，E的View All Internal Transactions锚点无href。未把这些标签伪造为可直接GET的专属端点，也没有执行其onclick。

## 字段覆盖矩阵

D为`lendle-default-executor-realization-20261019`，X单元为`lendle-execution-rights-distribution-20261019`；逐项机器可读版本见`field-coverage-matrix.json`。

| 账字段 | 已封存内容 | 仍缺/限制 |
|---|---|---|
| E资产 | MNT抓取时余额；9种token当前持仓显示、9个真实持有人href，含mETH（D/root/address.static-text L93–142、L861起） | 不是期初/末全资产表；token显示精度不冒充原始整数余额；没有协议债务/持仓状态认证 |
| X资产与顶层记录 | 当前MNT显示0；页面称196笔，仅静态首页最新25项；资产表/标签壳（X/root/execution-contract.static-text L93–124、L797起） | 不能因MNT0或资产表Loading称全部token/债权/负债为零；未收全X的196笔详情 |
| E顶层索引 | 既有8页400唯一hash；既有覆盖回执9月265项/133失败标签；hash、selector、block、日期/epoch、from/to、方向、native value、显示费及gas price | 相对提供者顶层索引完整；不是实体完整账、固定策略胜率或全部代币/内部流；没有全部nonce/input/receipt，也未归类自有资本流 |
| 全体费用精度 | 本轮静态读完8页全部400个showTxnFee单元，每页50，显示小数位6–8；单元只有class/style属性，无隐藏全精度fee属性 | **显示费不能当完整精确费用集。** 同一失败hash在page3 L1330显示`0.0686211`，单笔详情L125显示`0.068621109838654366 MNT`；本轮未相减/汇总。全页字面搜索也未取得该精确费用串；不排除未读取服务有精确数据 |
| 个案费用 | first-failure与creator详情有长精度Transaction Fee、Gas Price、Gas Used/Limit、L1/L2相关费字段、nonce/状态/身份；片段保存于individual-case-field-excerpts.json | 只是两例，非全月/全部运营费用；浏览器字段不是独立RPC receipt；未用Gas Used×Gas Price或L1/L2相加补造总费，未知错误42仍未知 |
| 成功案例代币流 | D/trace-owner已有19个Transfer：token/from/to/uint256原文/来源行；48事件及原片段保留Withdraw、Swap、42/46未知事件；E的mETH到账与F21款分列 | 未取得完整起末存量、279条逐内部调用或全月全部资产流；不把F21并入E。成功原页全头部在别的旧单元，本轮遵守范围未重开，因此不冒称本轮复核其全部gas原字段 |
| 期初末资产负债/资本流 | 当前概览与历史余额入口已定位；有选定交易/事件字段 | 本批没有已验收的精确边界时点全资产、债权、协议负债及主体归属数据集/端点。入口可见不代表数据已取得；没有从当前余额减资金推收益，也不声称别处永久不存在完整账 |

读取时E/X页面原件均有明确的抓取时点回执：E于2026-10-19 15:28:21–15:28:23 UTC，X于15:48:49–15:48:51 UTC，均原HTTP200。它们不是2026年9月期初/末状态。资产美元栏是提供者当前估值，不是美元兑现/历史本金。金额、数量、价格均未新增核算。

## 实际覆盖与交付

被动解析两地址页和E索引page1的实际锚点；逐页扫描page1–8全部费用单元及字面精度；读取两地址的相关静态概览/表头、既有顶层索引与日期回执、个案费用头部、成功案例Transfer/Event的字段结构及既有覆盖回执。未重新人工逐条审48事件、未打开原成功全HTML所在的第三单元、未请求任何链接或查询数据库。

`actual-href-candidates.json`、`token-and-tab-hrefs.json`保存所有命中href/HTML行；`index-fee-display-audit.json`保存全部400个原费用单元；`index-literal-precision-search.json`仅做字符串检查。Root告知的E CSV/历史余额403只记作协作状态，本Owner未重读其新HTTP原件，未换X/别名/网关或其他入口重取。

所有输入/输出哈希及覆盖边界见receipt.json。规则沿用PERMISSIONS-2026-10-14-v1 / ROUTING-2026-10-13-v4；实际model/effort UNKNOWN。未触及排除目录、私人身份、凭证、模型/回测、RPC/EVM或来源JS执行。
