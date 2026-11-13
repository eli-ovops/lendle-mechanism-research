# 九月历史网络毛收费：固定一次核验

固定三张HTML费用子span与receipt字段按冻结公式精确匹配，差额均为0最小单位；随后完成262笔E发出账，3笔他人发入排除。正式运行一次，无错误、公式改动、舍入拟合或重跑。

下列数字直接抄录已生成结果，单位MNT，无市场价格换算。

| 互斥主分类 | 笔数 | 网络毛收费 MNT |
|---|---:|---:|
| 执行失败 | 133 | 5.368549702315373718 |
| 成功创建 | 8 | 2.555505264923987174 |
| 其他成功 | 121 | 14.630007358587581131 |
| E发出合计 | 262 | 22.554062325826942023 |

X关联是同262笔的交叉视图：146笔，10.865529207152845412 MNT，不与上表另加。其他目标不被一概认定有关或无关。

冻结公式：gasUsed × effectiveGasPrice + receipt.l1Fee + gasUsed × operatorFeeScalar × 100 + operatorFeeConstant。l1Fee不再乘tokenRatio；1 MNT = 10^18最小单位只作精确显示。三账tooltip只明示including operator，未提前据此断言L1包含；精确对齐是本次结果。

全265只有type0/2；262出账为type2、3入账为type0；既存native-meta前缀检查与输入hash绑定。非零blobGasUsed同时具非空daFootprintGasScalar且无blobGasPrice，按Root/方法Owner已核固定源码是DA footprint分支，不另加第四项。这些是固定来源/分支条件一致性，不是独立认证9月实际节点binary或全部部署历史。

本结果为网络毛收费。第三方报销、补贴及最终经济负担仍UNKNOWN；无代币收入、美元估值、净利润、ROI、资金曲线或可复制性结论。

执行：2026-10-19T17:52:35.362168Z至17:52:35.426199Z；正式尝试1次，约0.064秒，峰RSS 32,587,776 B。预算为30秒/512MiB/新目录8MiB，总工作30分钟，均未超限。无网络、安装、来源代码/EVM、模型、回测、交易、付款、凭证或排除私人目录访问。actual model/effort UNKNOWN。

预检曾因外层span附USD按钮文字触发本地assert，仅修复实际费用子span提取并复用原件，留有preflight-parser-repair.json；当时未执行金额算术。收尾README生成另遇stdin编码SyntaxError，发生于解析阶段，未改正式结果；改用文本补丁保存说明，未重跑核算。

主要结果：three-bill-comparison.json、individual-network-bills.json、network-bill-summary.json、formal-execution-receipt.json。预检与冻结：preflight.json、blob-field-structure-preflight.json、three-fee-literal-preflight.json、source-input-manifest.json、run-plan.json/md、root-go.json。全部输出hash见final-delivery-manifest.json。
