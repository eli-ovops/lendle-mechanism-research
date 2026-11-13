# API3历史估值字段：原件准入

固定119个E收款交易hash全部在已保存HTTP正文中取得完整JSON对象，共128条清算对象（110个hash各1条、9个各2条）。默认成功0x5165…完整对象在原体字节2869623–2870371。hash、sender、blockNumber、blockTimestamp、清算logIndex及抵押/债务资产、borrower地址与既存receipt/normal全部匹配。同hash的gasCostUsd、bidAmountUsd、nativeTokenPrice原字段一致；不按128对象重复记119笔交易费用。

真实公开GET为https://oev-dashboard-backend-aws.api3.org/liquidations?dapp=lendle-mantle，来自已封存官方前端E10调用与Lendle配置，未猜参数、未执行JS。2026-10-19 18:19:34–18:19:38 UTC普通匿名curl收到HTTP200、严格TLS校验0、无重定向；因本任务8MiB单体上限截断，curl56。保留8,388,608B原始前缀，SHA256 5279cec1f3782c83e98d0d659308e945a4bf18c1c1e03c4e818e1f0f17681321。此前urllib在HTTP前TLS协议版本错误，HTTP UNKNOWN、正文0；不是来源拒绝或无数据。查询LOCAL_BLOCKERS后按Root确认改普通默认严格TLS curl，同URL一次。

整份响应未取得；前缀中完整解出11,154对象，末对象截断，未补括号或修造源。头中无Content-Length、无Content-Encoding，精确整体长度UNKNOWN；不从弱ETag推长度。dbLastBlock/syncDisabled尾字段未观察到。API3网络已停止，不追加下载、Range或猜分页。

| 实际同对象字段 | 已支持 | 未支持 |
|---|---|---|
| collateralAssets / debtAssets | 资产地址数组，与清算事件匹配 | 没有每资产原始数量或decimals |
| collateralSeizedUsd / debtRepaidUsd / incentiveUsd / protocolFeeUsd | 提供者估值整数字符串 | 后端估值源码、独立价格源、采价时点UNKNOWN |
| gasCostUsd / bidAmountUsd | 119个固定交易均有，同hash重复行值一致 | 不认证gasCostUsd包含全部实际网络收费或失败成本 |
| nativeTokenPrice | 同清算对象中的提供者标量；前端用作USD转原生币的除数 | 独立feed、round、价格观测timestamp未提供 |
| blockTimestamp / createdAt / updatedAt | 区块时间与既存normal一致，另有记录创建/更新字符串 | 不能把这些字段当已证实的采价时点或首次公开时间 |

已读当前前端显示链：USD值经Ds/Mwt/jte按18位格式显示；这只说明该前端的显示约定。未转换任何输入值，未除数推价或估值。Search profit是先前已核的提供者估算口径，不能当完整个人净利。

固定262笔费用hash只有119笔在前缀中有完整对象；未观察到的143笔在既存normal中为133失败、8成功创建、2其他成功。未见不能解释为完整响应不存在，但本源现有证据不足以给全部262笔提供同口径历史价格。119对象也没有直接估值最终E收款的字段；gross collateral USD与E末端残余Transfer是不同经济腿。

同hash+清算logIndex+抵押地址可将gross collateral USD与另行核实的gross清算数量建立符号对应。任何V/Q都会是提供者隐含价格，不能冒充独立市场报价；本轮不求商，亦不能用E残余数量替代gross seized数量作分母。固定119完整对象准入已取得真实进展；独立价格来源和全262费用估值仍未闭合。

主要证据：01/02获取原件与回执、static-source-excerpts.json、static-unit-display-excerpts.json、prefix-field-and-coverage-qc.json、fixed-cohort-complete-objects.raw-derived.json及cohort-identity-and-field-dimensions.json。仅来源/字段/身份检查，无金额乘加、逆推价格、利润、模型/EVM/交易或私人行情访问。实际model/effort UNKNOWN。
