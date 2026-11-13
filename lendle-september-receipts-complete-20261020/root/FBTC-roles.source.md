> For the complete documentation index, see [llms.txt](https://docs.fbtc.com/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.fbtc.com/security/roles.md).

# Roles

## System Roles

### Merchant

An entity or a party that mints FBTC from BTC and burns FTBC into BTC is known as a merchant. A merchant can be an institution, permissioned protocol, or network. Each merchant will have to fulfill certain requirements and complete Know Your Business (KYB) before onboarding. Merchants play a pivotal role in the distribution of FBTC. If you want to know current merchants information, please check [here](/security/bitcoin-reserve-address.md).

### Security Council

Function’s Security Council is a group of independent and trusted institutions that currently include Antalpha, Mantle, and Cobo. The Council acts as the governance and oversight layer for FBTC by:

**Safeguarding smart contracts**

* The council reviews and audits code before deployment to identify vulnerabilities or potential exploits.
* Coordinated external and internal audits to maintain high security standards.

**Approving key upgrades and improvements**

* Every major upgrade, such as contract updates, logic modifications, or integration of new systems must be approved by the Council.
* This approval process is secured through TSS (Threshold Signature Scheme) and MPC (Multi-Party Computation) features, ensuring that no single party can execute an upgrade or transaction independently.

**Overseeing custody of $BTC to ensure $FBTC remains 1:1 backed**

* The Council oversees the mint and burn process, and performs regular reviews and audits of reserves.

**Maintaining the decentralized integrity of the system**

* Control cannot be concentrated in the hands of a single party.
* Decisions are made collectively.
* This structure preserves decentralization while maintaining reliability, compliance, and operational integrity at the institutional level.

### Custodians

The custodians refer to the financial institutions that hold customers' assets for safekeeping to prevent them from being stolen or lost. The custodian has responsibility for the care, preservation, and management of the assets on behalf of the customers. In the case of FBTC, the custodians manage users’ assets in an MPC address whose key shares are held by several trusted institutions. Custodians guard the user-deposited BTC and conduct the FBTC issuance under restricted risk control in a decentralized way.

## Contract Roles

### Contract Owner (Owner)

**Responsibilities**:

* Safe MultiSig
* Holds the highest authority to make significant changes and manage the contract.
* Executes contract upgrades and sets new implementation contract addresses.
* Adds or removes merchants.
* Sets fee models and fee recipients.
* Pauses or resumes contract functions when necessary.

### Minter

**Responsibilities**:

* Responsible for minting and burning FBTC tokens.
* Confirms users' minting and burning requests.
* Ensures that the circulation and supply of tokens comply with system rules.

### Pauser

**Responsibilities**:

* Has the authority to pause and resume contract functions.
* Pauses critical operations of the system promptly when potential risks or vulnerabilities are detected.

### Safety Committee Member

**Responsibilities**:

* Safe MultiSig
* Handle emergencies by executing emergency burn operations to protect the system and user assets.
* Review and respond to potential security threats.


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://docs.fbtc.com/security/roles.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
