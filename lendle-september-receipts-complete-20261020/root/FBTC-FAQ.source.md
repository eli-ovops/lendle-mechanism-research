> For the complete documentation index, see [llms.txt](https://docs.fbtc.com/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.fbtc.com/more/faqs.md).

# FAQs

#### Q: Why do I have different addresses in my wallet, and what are their differences?

**A:** Bitcoin addresses are 26-62 alphanumeric character identifiers, available in various formats:

1. **Legacy address (P2PKH)**: Begins with "1", case-sensitive, original and most common format, but less efficient and costlier due to larger transaction sizes.
2. **Script address (P2SH)**: Begins with "3", case-sensitive, supports additional rules and functionalities, commonly used for multi-signature addresses.
3. **Segwit address (P2WPKH)**: Begins with "bc1q", case-insensitive, uses error-correcting codes, improves scalability and reduces transaction fees with efficient script language (Segregated Witness).
4. **Taproot address (P2TR)**: Begins with "bc1p", case-insensitive, enhances privacy, scalability, and scripting capabilities, allowing for signature aggregation and making complex transactions more efficient and cost-effective.

**Q:** **Can anyone mint/burn FBTC?**

**A:** Only merchants who have completed the KYC/AML process are eligible. U.S. users are not permitted to use FBTC. For onboarding, please visit [here](https://fbtc.com/register-qualified-users).

**Q: Are there any fees for using the bridge or minting and burning FBTC?**

**A:** There are two fees you need to pay:

* **Bridge Fee**: Users need to pay a fee for using the bridge.
* **On-chain Gas Fee**: Users also need to cover the gas fees for transactions on the blockchain.

**Q: How is the 1:1 peg maintained?**

**A:** We ensure that the custodial wallet address always holds an equivalent amount of BTC to the FBTC0 on-chain. This guarantees that users can always exchange BTC and FBTC at a 1:1 ratio.

**Q: How is the security of the protocol ensured?**

**A:** The protocol contracts are stored in audited contracts and managed by licensed MPC wallet custodians. Our custodians and MPC wallet partners adhere to the highest security standards and are widely adopted by industry institutions. Using MPC custodial wallets ensures that BTC assets remain off-exchange, mitigating risks associated with exchange incidents.

***


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://docs.fbtc.com/more/faqs.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.
