# 历史网络账单：公式与分支准备审阅

**must_fix=[]，固定公式获静态支持；只允许按既定三账作条件性来源一致性核验。** 本Owner尚未代入计算账单，也未验收全262笔费用结果。

1. 固定op-geth commit `c739e50e35071247cf459cbcbbbfc4cf989b4c57` 的 `source-owner/08-rollup-cost-go.source` L64/L437–442明确operator为 `gas × scalar × 100 + constant`；`root/state-transition.source.go` L359–383先按GasLimit预购、L846–878处理退款/floor、L922–938及L1050–1065将operator结算到最终gasUsed并退差额。执行gas的剩余预购额另退，不能把GasLimit预扣额当最终收费。`06-receipt-go.source` L426–427与`07-ethapi-api-go.source` L1923–1929连接最终gasUsed及effectiveGasPrice；`root/state-processor.source.go` L240–242已把ratio乘入receipt.L1Fee，L252–258输出operator参数。因此三项相加的固定源码解释成立，l1Fee不再乘ratio。

2. 非零blobGasUsed不是type3的充分条件。`07-ethapi-api-go.source` L1959–1963明确Jovian将其复用为DA footprint；L1979–1981仅type3输出blobGasPrice。`08-rollup-cost-go.source` L473–505说明DA footprint服务区块限额及base-fee更新，未在所读路径定义额外第四项交易收费。三份固定原件均type2、带DA scalar而无blobGasPrice，符合该表示；正式全265应逐项核这种字段组合，遇不支持分支即停，不据字段名增费。全265为262个type2发出和3个legacy入账；后者不能算入E付费总额，也不能误写全体type2。U原生meta前缀检查与源码L100–150支持在固定源码下排除该native sponsorship，不能排除链内外报销或认证历史实际部署。

3. 独立实读事前固定成功、失败、部署三笔请求/原SSE/parsed及对应explorer原HTML，源hash、整体对象、身份与原生MNT文本提取均通过，见fixed-three-originals-check.json。spanTxFee小数点被b标签分开不是数值缺失；tooltip只显式写包括operator，L1另列，不能仅靠tooltip认定此栏含全部L1。必须等待冻结公式与三张原文精确一致；任一差异保留并停止，不能改公式、舍入、换案例或补零拟合。三账精确一致至多加强公开提供者/浏览器/固定源码一致性，不升级为独立主网二进制认证。scope-and-acceptance.md已明确这个条件层级，历史版本未独立认证不被冒称已解决。

后验将核3笔他人入账排除、失败/成功部署/其他成功互斥、X仅交叉视图不叠加、费用参数零与缺失区别、网络毛收费与最终经济负担区别；不以账单通过推净利或复制优势。零新网络、来源代码/EVM/模型/回测执行、费用算术、交易、账户/凭证或私人行情目录访问。实际model/effort UNKNOWN。开始17:45:58 UTC，30分钟截止18:15:58 UTC。
