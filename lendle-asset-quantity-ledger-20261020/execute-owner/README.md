# 固定265笔：标准Transfer原数量账

唯一正式运行完成，无错误、重跑、换样或金额拟合。完整265笔共5930条日志，2164条符合标准ERC20 Transfer布局；事件键为chainid+交易hash+logIndex，未按交易hash合并事件。未见格式异常或重复身份。

E在这265笔中有119条转入、0条转出、0条自转，涉及9个发币合约。以下均为原始uint256最小单位，直接抄录已生成结果；未按decimals转换、未乘价格。供方标签仅供辨认，合约才是分账标识，不是发行人或精度独立认证。

| 供方标签 | 发币合约 | 转入原量 | 转出原量 |
|---|---|---:|---:|
| AUSD | 0x00000000efe302beaa2b3e6e1b18d08d69a9012a | 1255162 | 0 |
| USDC | 0x09bc4e0d864854c6afb6eb9a9cdf58ac190d0df9 | 1297780 | 0 |
| USDT | 0x201eba5cc46d216ce6dc03f6a759e8e766e956ae | 1552664 | 0 |
| USDe | 0x5d3a1ff2b6bab83b63cd9ad0787074081a52ef34 | 65336443242224103 | 0 |
| WMNT | 0x78c1b0c915c4faa5fffa6cabf0219da63d7f4cb8 | 4904995940405552767 | 0 |
| FBTC | 0xc96de26018a54d51c097160568752c4e3bd6c364 | 1231 | 0 |
| mETH | 0xcda86a272531e8640cd7f1a92c01839911b90bb0 | 1566380606566258 | 0 |
| WETH | 0xdeaddeaddeaddeaddeaddeaddeaddeaddead1111 | 91773677003928 | 0 |
| cmETH | 0xe6829d9a7ee3040e1276fa75293bde931859e8fa | 159868373938657 | 0 |

F21另列78条转入、0条转出，涉及8个合约，完整原量见F21-event-ledger-and-token-totals.json。F21不并入E，也不从E收款中再扣其原量。119条正E事件与旧解释的hash、logIndex、合约、from/to、raw hex全部匹配。

固定119笔清算的实际liquidator由同池LiquidationCall地址字段核定，共5个地址，未假定L=X。119个同笔×L账保留所有触及L的标准Transfer，包括aToken及不同代币，不合并不同主体。93个账的全部代币日志净额为0；另有31行代币净额非零，全部保留，见nonzero-liquidator-rows.index.json及完整fixed119-per-receipt-liquidator-books.json。不能把119笔全部称为精确闭合，也未因差额小而抹零或移除。所有零/非零行均在主账，索引仅复制已有结果便于定位。

只把标准Transfer作为数量腿；BalanceTransfer、Burn、Withdraw、Swap及协议费字段不重复加成额外腿。E、F21、各L分账是不同主体投影，不相加为一个主体；L的同笔偿债/回调腿不从E最终收款直接再扣一次。

本结果是固定265份receipt内的标准Transfer日志量，不是完整经济净收入、余额证明、无本金证明或利润。未覆盖期初末余额、rebase/非标准变化、原生币/internal、范围外交易或主体所有权；L日志平衡不等于没有外部成本。旧网络账输出未打开或重算，费用与不同代币原量不混算。无美元估值、净利润、ROI或资本曲线。

资源：正式尝试1次，约0.051秒，峰RSS 23,150,592 B，单线程；目录总量见final-delivery-manifest.json，低于8MiB。无网络、安装、来源代码/EVM、模型、回测、交易、付款、凭证或排除私人目录访问。actual model/effort UNKNOWN。

主要文件：共享源事件池event-pool.raw.json；E/F21逐事件及分合约方向原量账；prior119-event-identity-reconciliation.json；119同笔liquidator账及限定119范围的分地址合约总量；quantity-ledger-summary.json；formal-execution-receipt.json。冻结输入、Root GO及全部输出hash见run-plan.json、root-go.json和final-delivery-manifest.json。
