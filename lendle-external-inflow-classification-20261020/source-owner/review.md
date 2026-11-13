# 三笔外部 MNT 转入：地址标签有新增证据，用途仍 UNKNOWN

**本轮不能把三笔转入追加认定为经营收入、费用报销或补贴，也不能认定为 E 自有资本。** 已有原件与两个来源地址页没有提供这些转入的明确用途或实益所有权说明。保留为“用途未分类的外部原生 MNT 转入”；这一未知不等于它们绝非经营所得。本轮未改动或重算任何既有账。

既存 E_normal 与265 receipt registry中的三笔均逐身份匹配。**normal 原件的 input 均为 `0x`；receipt 仅核身份、status=`0x1`、type=`0x0`、logs=`[]`。receipt 不含 value/input 字段，未用于独立核额。** 两类来源均没有可供分类的合约事件或输入备注：

| hash | from | 字段来源 | 用途结论 |
|---|---|---|---|
| `0xca6fce434a1f146b8c8345822d1ad50f38a1770359b07c1c955505b3337da62f` | `0x91604f590d66ace8975eed6bd16cf55647d1c499` | normal input=`0x`；receipt logs=`[]` | UNKNOWN |
| `0x65c24c5811d35c5d7e0cd9b0648a88f01a4e049e07f1b564edc00dc5e1ab9768` | 同上 | normal input=`0x`；receipt logs=`[]` | UNKNOWN |
| `0x5c2cec8f68d1e9b2562530b07466861838d3044f1aee8607382b4b48ede0e7b1` | `0x5c30940a4544ca845272fe97c4a27f2ed2cd7b64` | normal input=`0x`；receipt logs=`[]` | UNKNOWN |

**新增公开来源事实。** 2026-10-19 18:59:05–18:59:08 UTC，以下两地址页各一次普通严格TLS GET，均HTTP200、无重定向：

- [`0x91604f…`](https://mantlescan.xyz/address/0x91604f590d66ace8975eed6bd16cf55647d1c499)：标题及头部没有自身公共名称标签，meta description标为 `Address (EOA)`。More Info 的 `Funded By: Gate 1` 提示定义是首次给这个来源地址提供 MNT 的地址/交易（HTML byte68011起），不是给 E 的两笔付款用途，也不能把本地址本身称为 Gate 交易所。原体581739B，SHA256 `bcba478307fa9fb0427dd4987d14f8746476f26171e6a288a3a0d1b0dcb104f3`。
- [`0x5c3094…`](https://mantlescan.xyz/address/0x5c30940a4544ca845272fe97c4a27f2ed2cd7b64)：当前公共标签为 `MEXC 34`、类别 `Exchange`，meta description同样标为 `Address (EOA)`。页面明示标签依据 hildobby compilation（byte56073），公共名标签链向mexc.com（byte56786）。这只是 explorer 的地址归类，未独立核交易所声明、E的交易所账户、提款人或资金实益归属；不能据此证明 E 自有资金提款，更不能证明该笔是交易所支付的经营报酬。原体528375B，SHA256 `f5a3a37869ce37ec1a66fb028f98a718c2d7769db38446b9b6feaafad66870b6`。

地址类型是当前 explorer 提供者标记，未独立核代码或历史状态。没有读取两来源的完整交易史，没有追自然人、当前余额或其它付款者；页面所附首屏记录及动态资产字段未用于金额/归属推论。标签链接、Funded By链接不能直接说明固定三笔的性质，故未为耗尽预算继续读取Dune、交易所主页或祖先地址。

已用2/4公开动作，网络已停止；HTTP原体共1110114B，小于2MiB总量及单体1MiB限制。本轮没有金额乘加、估值、重价、费用/利润重算、模型/回测、EVM、账户/凭证、注册、安装、付款或外发。实际 model/effort 为 UNKNOWN。每笔身份及封存原件路径/哈希、页面原始段落位置见 `address-label-and-inflow-evidence.json`；完整交付哈希见 `receipt.json` 与 `manifest.json`。
