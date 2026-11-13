# 固定历史网络毛收费：一次正式运行计划

当前状态：输入与解析器预检已就绪，尚未执行任何费用乘加或金额聚合；只在 Root 明确 GO 后执行一次。固定原265集合不换样，262 E 发出计账、3 Legacy 他人发入排除。

公式固定为最小单位整数：execution = gasUsed * effectiveGasPrice；operator = gasUsed * operatorFeeScalar * 100 + operatorFeeConstant；total = execution + receipt.l1Fee + operator。l1Fee 不再乘 tokenRatio；1 MNT = 10^18 最小单位仅用于精确显示，不做价格换算。

事前门：全265唯一且与normal同集合；262出账type2、3入账type0；无deposit类型/字段或原生Meta前缀。全265非零blobGasUsed同时具非空daFootprintGasScalar且无blobGasPrice。Root/方法Owner确认固定源码该分支blobGasUsed是DA footprint展示，不额外加第四项；未来遇不支持组合即停。此条件检查不认证9月实际binary或全部部署历史。

先按 default_success、fixed_failure、linked_creation 固定顺序核三张原HTML费用子span的可见MNT原文，精确到最小单位，不舍入。tooltip只明确including operator，不能预设包括L1；三账必须全部精确匹配才继续。任一不匹配即保存已尝试差异及未尝试案例，STOP，不算262聚合、不换公式/账单/样本、不重试。

三账全过后，逐262唯一E发出各核一次；三账缓存复用，不重算其金额。主分组互斥：执行失败；成功创建；其他成功。X地址关联/其他目标是同262的交叉视图，不与主组合计相加。3incoming保留排除身份，不把他人发送费用扣给E。

输出只是该固定来源/公式下网络毛收费及三账一致性；第三方报销、补贴、独立历史部署仍UNKNOWN。无代币收入、价格换算、净利润、ROI、资金曲线或容量结论。零网络/安装/EVM/来源代码/模型/回测/交易/付款/凭证/排除私人目录访问。

预算：总工作截至2026-10-19T18:16:12.703793Z；唯一正式尝试30秒、512MiB RSS、单线程、新目录总8MiB；创建排他attempt锁，失败即停。仅运行自有标准库解析器，Root GO回执绑定本run-plan.json与正式脚本hash。预检本地HTML外层含USD按钮导致一次AssertionError，已按真实费用子span修复并复用原件；这不是金融重跑，三份原HTML未改变。
