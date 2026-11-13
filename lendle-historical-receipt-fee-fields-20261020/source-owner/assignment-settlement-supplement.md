# 补充：Receipt.L1Fee赋值与实际费用结算路径

**前轮唯一静态源码赋值缺口已关闭。** 新读的两份同commit官方源码，将执行前TokenRatio、MakeReceipt赋值及RPC输出链连接起来：普通非deposit、Arsia/Fjord分支的`receipt.l1Fee`已包含MNT换算，不应再乘一次TokenRatio。此补充只更新源码认识，旧报告/回执原样保留；主网历史部署、提供者实际版本与个案完整费用/付款归属仍未独立认证。

## 1. 赋值链现已可定位

固定commit仍为`c739e50e35071247cf459cbcbbbfc4cf989b4c57`。

- [core/state_processor.go L166–188](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/core/state_processor.go#L166)：执行交易之前从GasOracle状态读取TokenRatio，执行后把同一值传入MakeReceipt，未改用后来某时刻的当前比率。
- [L202、L213–258](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/core/state_processor.go#L213)：GasUsed来自result.UsedGas；对非deposit交易记录TokenRatio。在通常Arsia/Fjord分支，L240–242用Fjord费用乘传入的TokenRatio，**直接赋给receipt.L1Fee**。首个Arsia特殊分支L234–237和旧分支L260–263调用前轮已读的L1Cost（内部也含ratio）。L252–258把operator scalar/constant放入receipt。
- 接前轮api.go L1933–1956的直接序列化，源码层面“收费模型/捕获ratio→receipt.L1Fee→RPC字段”桥接已补齐。前轮对这条赋值链的UNKNOWN不再作为未读缺口。`l1Fee`采用该路径已换入native MNT最小单位；l1GasPrice等参数与其不能混为同一单位，更不能把GasPriceOracle估算提示的额外换算再次套到这里。

MakeReceipt先按执行结果标记成功/失败，再进入非deposit费用字段赋值，没有仅因执行失败就跳过这些字段；不据此替代个案实际receipt或宣称所有失败情形相同。

## 2. GasLimit预扣与最终gasUsed结算不能混淆

[core/state_transition.go L359–383](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/core/state_transition.go#L359)先以GasLimit准备执行费，并在Arsia分支加入L1成本及按GasLimit取得的operator预扣额；L371–375注释明确区分L1不按余gas退款与operator按实际使用退款。

随后L846–878有gas refund和数据floor调整，L943返回最终gasUsed；[L922–938](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/core/state_transition.go#L922)复用L1成本、调用refundOperatorCost，再按最终gasUsed给operator费接收方记账。[L1050–1065](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/core/state_transition.go#L1050)分别取GasLimit与gasUsed对应的operator成本，退还二者差额；普通剩余执行gas也另行返还。因此**不能把按GasLimit算出的预扣额称为最终operator实付**。结合前轮rollup_cost.go的`gas × scalar × 100 + constant`，最终结算输入是代码指定的gasUsed；本轮只读规则，没有执行公式、代入任何参数或算费用。

## 3. 付款者必须按交易路径识别

L417–446含MetaTxParams赞助余额检查；[L468–481](https://github.com/mantle-xyz/op-geth/blob/c739e50e35071247cf459cbcbbbfc4cf989b4c57/core/state_transition.go#L468)实际在赞助分支分别从GasFeeSponsor及msg.From扣款，普通无meta分支才从msg.From扣预购额。Deposit/system、估算或call模式也有专门条件。故“仅把费用归于实际付款者”仍成立，但**from不能不经分类就当全额费用承担人**。本Owner未解析三个样本的MetaTxParams或重建其分担/退款，不认证任何个案赞助比例或主体账。

## 获取与边界

本轮零网络；仅读Root已取得的两份源码及各自acquisition.json，均固定同commit，原GET在2026-10-19 16:47:32 UTC、HTTP200。state-processor原文16040B、SHA256 `410e1b785e44d2ad08497cfa8457c28f418004645334b967dea1af7ceb92eaf4`；state-transition原文49142B、SHA256 `3166b1308dbe58e8761df8ec43a30e43c2f976d6b58f2906634f01bb7a182435`。实际读取processor L149–268、transition L330–497/L800–947/L1015–1074及字段窄rg；未冒称整仓库审阅。

这里只证明固定源码路径的定义；没有运行/编译Go、EVM/节点/RPC、金额乘加/换算、模型/回测或交易。三份Root实际receipt已证明这些字段现可取得，仍不是全9月记录及所有网络费用/主体付款归属的证明。主网4月计划与Sepolia限定手册的范围差异继续保留；源码发布不认证9月逐块实际版本或provider实现。旧报告与回执不改，实际model/effort UNKNOWN。
