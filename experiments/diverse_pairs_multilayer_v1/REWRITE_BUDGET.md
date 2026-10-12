# Rewrite resource record: first 50 pairs

11 October 2026. This is an explicitly authorized current-session pilot.

## Model choice

Configured rewriter alias: gpt-6-luna, low reasoning effort. Each worker receives
only the rewrite contract and a small source batch, with no inherited research
chat history. Base batches contain 17, 17 and 16 sources. Two unusable sources
are retained as rejected drafts and replaced from deterministic same-source/task
reserves. Two early rows received one bounded content-preservation revision.

The parent spawn tool supplies the model alias. A dated provider snapshot and
per-worker billable token usage are not exposed. No independently configured
API, API key, newly downloaded generation model, purchased compute, or account
quota reset is used. This route still consumes the account's Work/Codex usage.
The user authorized this 50-pair batch, not a full 1,000-source rewrite pass.

## Actual quota observations

- Current signed-in Codex plan reported by the app: Pro.
- Before rewrite work: weekly usedPercent=10 (90% remaining).
- After the first 17-row batch and accompanying preparation: usedPercent=11.
- The difference includes root-agent work and other tasks sharing the account;
  percentage rounding and concurrent usage prevent exact rewrite attribution.
- This account readout does not confirm a message-count cap for a different
  ordinary ChatGPT Chat model. Message limits and Work/Codex allowance differ.

At the completed-packet observation, the weekly bucket was 12% used (88%
remaining). The observed 10% to 12% change includes preparation, root-agent
coordination, rewriting, retries and other shared-account activity. No exact
cost-per-pair or included-message conversion is claimed. API list prices are
not used to estimate subscription allowance.

## Token controls and separate costs

Avoid importing the long research history into each worker. Do not generate new
source answers or repeat the old experiments. Run deterministic text checks and
local tokenizer checks without model forwards. Retries are bounded; failed
drafts remain available. Natural content rewrites are not replaced by templates.

The report includes token-length proxies using the cached Qwen tokenizer for
technical input budgeting only; these are not OpenAI billable token counts.
The source transfer is approximately 11.3 MB for original HelpSteer2 plus bounded
WildChat parquet range reads, not a full million-conversation download. Actual
WildChat network byte totals are not available and should not be invented.

The final 50-pair packet contains 100 responses, approximately 26,090 response
tokens under Qwen's tokenizer; the 50 source responses contain approximately
13,420 tokens under that same tokenizer. These exclude prompts, tools, reasoning,
coordination and discarded drafts and cannot be used as a billable total.

The first packet remains human_review=pending. Subsequent expansion depends on
the user's content audit and a fresh usage estimate, rather than a claim that
lower-cost rewriting has already met the study's quality requirements.

## User-requested stronger-hedge revision

Revision 2 uses the same three short-context GPT-6 Luna workers for 17, 17 and
16 existing items. Only hesitant wording changes; the 50 source texts and
confident versions are frozen. It does not repeat source acquisition, Qwen
inference, historical experiments or probe fitting. Additional allowance is
consumed by rewriting and bounded repairs; the historical 10% to 12% observation
above refers to the first packet, not this revision. No new independent API
or paid compute is used. First-packet text, checks and browser reviews remain
available in the private revision archive.

Protected-string and length checks are engineering screens, not a guarantee
that each edit preserves meaning. Repeated phrasing remains an audit item;
clearer hesitation alone does not validate the eventual confidence readout.
All revised pairs still require actual human review.

## Official references checked for this choice

- [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna): focused,
  high-volume tasks. This description does not certify content preservation.
- [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): model
  configuration and the additional usage from independent workers.
- [Work/Codex pricing](https://learn.chatgpt.com/docs/pricing): shared usage,
  task-dependent allowance and distinction from API token prices.
