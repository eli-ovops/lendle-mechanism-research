# Mantle v1.5.4历史receipt费用字段：静态来源核验

**结论：固定v1.5.4源码明确支持历史receipt的L1/Operator字段序列化，且Arsia收费函数内部已做TokenRatio换算；发送前EstimateTotalFee与历史receipt不是同一种证据。** 已读范围仍缺`Receipt.L1Fee`从收费函数取得值的实际赋值调用点，不能据已读文件单独认证任意提供者历史receipt的完整同源/单位映射或9月实际部署。Root另已取得三个历史receipt字段，这推翻“当前这些字段一概不可得”；本Owner没有重复取账户原记录或计算费用。

## 版本与主网适用性

[官方主网v1.5.4 changelog](https://docs.mantle.xyz/network/for-node-operators/network-updates/changelogs/mantle-v2-v1.5.4-arsia-upgrade.md)与[GitHub发布原件](https://github.com/mantle-xyz/mantle-v2/releases/tag/v1.5.4)都写明Mainnet Arsia，计划在2026-04-22 07:00 UTC激活；release API的published_at为2026-04-08T07:49:53Z。`mantle-v2/v1.5.4/go.mod`第325行实际replace到`github.com/mantlenetworkio/op-geth v1.5.4`。本次[官方op-geth tag解析](https://api.github.com/repos/mantle-xyz/op-geth/commits/v1.5.4)取得完整commit `c739e50e35071247cf459cbcbbbfc4cf989b4c57`，committer日期2026-04-07T02:57:08Z；下述三个Go文件全部用该commit固定URL获取。

**冲突保留：** 已封存[费模型手册](https://docs.mantle.xyz/network/system-information/fee-mechanism/fee-model-handbook-after-arsia.md)仍明确“仅Mantle Sepolia”；[升级说明](https://docs.mantle.xyz/network/introduction/updated-notices/arsia-upgrade-mantles-new-fee-model-and-op-stack-alignment.md)开头也仍指Sepolia。主网changelog/release提供另外的主网发布/计划证据，不能抹去手册范围标注；发布/计划和源码tag均不是主网9月逐块实际升级、参数值或提供者节点版本的独立认证。

## 已证的字段与单位边界

[api.go固定源码](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/internal/ethapi/api.go#L1887)的`GetTransactionReceipt`读取指定交易所在块的既有receipts，进入`MarshalReceipt`，并非调用估算接口。完整序列化函数在1913–1990行。

| 字段 | 固定源码语义 | 单位/限制 |
|---|---|---|
| `gasUsed`、`effectiveGasPrice` | api.go L1922/L1929从receipt直接输出；receipt.go L424–427有上下文派生值 | gas数量、每gas的native最小单位价格；不是已经存在的独立totalFee。未代入任何案例相乘 |
| `l1GasUsed`、`l1GasPrice` | api.go L1933–1934直接输出receipt字段，使用hexutil.Big | 前者为L1数据gas计量，非币数量；后者为L1价格参数，不能直接当MNT已付金额。receipt.go L84提示Fjord之后l1GasUsed已deprecated；源码RPC名称为l1GasUsed，不是浏览器/MCP的L1Gas，未认证二者映射 |
| `l1Fee` | api.go L1935直接序列化receipt.L1Fee；receipt.go有存储编码/恢复字段 | Arsia L1收费路径已换入native MNT单位（见下）；序列化本身不再乘tokenRatio。**赋值调用点尚未读到**，所以提供者历史字段具体同源/单位仍需该桥接；不能因GasPriceOracle估算手册而对receipt字段自动再乘比率 |
| `operatorFeeScalar`、`operatorFeeConstant` | api.go L1952–1956在非nil时以hexutil.Uint64输出；receipt.go L89–90及L159–160保留参数 | Scalar是系数，Constant与收费函数结果同为native最小货币单位；两者不是一笔已给出的operatorFee金额。指针非nil但数值零仍会输出；缺字段不能无依据补零 |
| `tokenRatio`、其他L1 scalars | api.go L1939–1950直接输出已有参数；l1FeeScalar是条件输出的字符串 | 参数不等于额外一笔费用；是否已有换算应沿生成路径核，不能重复计费 |
| `totalFee` | 在已读的完整MarshalReceipt映射中没有该独立字段，也没有计算总费用 | 不把别的方法/工具估算值冒充历史receipt totalFee；不对其他版本或提供者作永久不存在断言 |

RPC大整数/uint字段在此通过hexutil类型序列化，不能把它们当已经换成MNT十进制或Gwei的展示字符串。源码称货币最小单位为wei；结合Mantle官方手册的native gas token=MNT，这里的native收费单位应区分于Ethereum L1 ETH单位。没有实际换算任何金额。所有Optimism附加费用字段还受非deposit交易及指针/升级分支条件约束，不能要求任意历史/特殊交易都有相同字段。

## 收费路径、估算与单一未闭合点

[rollup_cost.go固定源码](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/core/types/rollup_cost.go#L144) L144–154把L1CostFunc说明为状态转换中的rollup收费函数；L160–217按块时间选Arsia前后路径。L310–319的Arsia函数先取Fjord成本，再乘当前TokenRatio，返回fee与gasUsed；L220–244的旧路径同样包含ratio。因而“L1收费函数返回值尚未转成MNT”与此源码不符。L437–443的operator收费函数是符号规则`gas × scalar × 100 + constant`；这里没有另乘TokenRatio或套其他OP分叉常见的缩放公式。仅说明源码算式，未执行、代入或计算费用。协议内部采用压缩大小拟合，不应因此把所有历史费用字段降格成发送前预测；真正扣款/receipt赋值链仍要完整核对。

反之，[api.go L1095–1234](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/internal/ethapi/api.go#L1095)明确将`EstimateTotalFee`描述为发送前费用估计、返回wei。它使用`DoEstimateGas`、输入/建议价格、未签名交易成本数据和operator函数，并对未签名交易额外补FastLZ字节；拒绝pre-Arsia及blob场景。这不能代替某笔已经发生交易的receipt或独立实付总额，也不能直接套手册简式重建历史收费。

**唯一关键源码缺口：** 已读receipt.go只见`r.L1Fee = stored.L1Fee`等持久化恢复；api.go只读/序列化，rollup_cost.go定义收费函数。尚未定位实际把该费用赋给Receipt.L1Fee、以及历史具体节点路径的调用点。于是本轮明确支持“该固定源码Arsia收费函数已乘ratio、receipt输出不再换算”，但不独立认证“任何历史provider.l1Fee必然来自这一路径”。三份Root已取得的receipt字段是可得性新证据，非本Owner已审的全9月完备数据集。

## 获取与实际覆盖

新公开预算保守按2个定向search query+6个普通GET计8/8，均已终止，无新网络。六GET全部HTTP200：release API 4981B、go.mod 16862B、op-geth commit API 5322B、receipt.go 22206B、api.go 94542B、rollup_cost.go 22736B；UTC为2026-10-19 16:44:09–16:45:16，逐件URL/UTC/hash在旁置receipt与总receipt.json。search原结果另存，HTTP/精确查询时刻未由工具披露，记录有界读取窗口而不伪填。无日期的三份官方文档未冒称发布日期。

完整读三份既有文档及v1.5.4 release正文；go.mod只定位依赖replace；commit API只读版本/日期/文件元数据。源码实际覆盖：receipt.go结构/序列化覆盖类型/持久化段（L54–119、L147–161、L421–433、L472–503、L575–588），api.go估算与完整receipt映射（L1095–1234、L1887–1990），rollup_cost.go收费选择/计算/参数提取（L144–244、L310–470、L538–542）；另外rg窄查相关字段全文件。没有冒称读完整个项目、编译运行或认证9月链状态。

仅自有stdlib抓取与文本/哈希整理；没有运行来源Go/JS、节点/RPC、eth_call/estimate/trace、模型/回测、金融核算、交易或付款，没有读凭证/排除目录或修改其他Owner。实际model/effort UNKNOWN。
