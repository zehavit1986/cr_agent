# 002 — Remove Import-Time Side Effects from the Messages Example

Status: draft
Owner: zehavit
Last updated: 2026-10-08

## Goal
Apply the code-review suggestion to make importing `10-messages.py` safe: imports must not
load environment variables, construct an API client, make paid API calls, or print output.

## Scope
- Update the `10-messages.py` example identified as the first target in plan `001`.
- Move executable setup and the two-turn example flow into `main()` behind an
  `if __name__ == "__main__":` guard.
- Construct the Anthropic client inside `main()` and pass it to `chat()` rather than relying
  on a module-level client.
- Keep the message-building helpers importable and free of external side effects.
- Do not change the reviewer application or address unrelated findings from the report.

## Assumptions
- The example source is maintained in the separate `ai4dev-agent-files` project and must be
  available when implementation begins.
- Running the example directly should preserve its current two-turn conversation behavior.
- The source can be tested without real API credentials by injecting or mocking the client.

## Open Questions
- Q1: Should the example also add friendly API error handling while moving setup into `main()`?
  Recommended: keep this plan limited to import safety; track error handling separately.
- Q2: Where should the regression test live? Recommended: next to the example in its owning
  project, using mocked dependencies and no network access.

## Steps
1. Check out the `10-messages.py` source in its owning project and confirm its current CLI
   behavior.
2. Move dotenv loading, client construction, conversation setup, API calls, and output into
   `main()`; add the standard main guard.
3. Change `chat()` to receive the client explicitly and keep helper functions free of global
   client state.
4. Add regression tests proving import causes no output or API calls and mocked direct
   execution preserves the two-turn message flow.

## Validation
- Import the module with Anthropic and dotenv calls instrumented; assert no client is created,
  no API method is called, and no output is written.
- Run the example's tests with `python -m pytest -q`; all tests pass without network access or
  an API key.
- Run `10-messages.py` with a mocked client and verify both responses are printed and appended
  to the conversation history in order.

## Risks
- Moving initialization can accidentally change direct-execution behavior or message ordering.
- The source lives outside this repository, so implementation and test results depend on
  access to its owning project.

## Rollout Order
Update the example, add the import-safety regression test, run offline validation, then verify
the example's documented direct-execution workflow.

## Rollback
Revert the example and its regression test together if direct execution no longer preserves
the existing conversation behavior.