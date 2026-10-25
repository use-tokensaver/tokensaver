# tokensaver

**Fewer tokens, every page.** A local MCP server that turns web pages, PDFs, Office
files and JSON into compact text for your coding agent.

A 183,000-token Wikipedia article becomes 19,000 — or a 250-token outline, so the
agent reads only the section it needs.

- **Local.** One Go binary. No API keys, never calls an LLM, no telemetry unless you opt in.
- **Nothing else to install.** PDF support is built in. Chrome is optional (for pages that need JavaScript).

## Install

```bash
brew tap use-tokensaver/tokensaver
brew install tokensaver
```

No Homebrew, or on Windows? Download a binary from
[Releases](https://github.com/use-tokensaver/tokensaver/releases) and put it on your `PATH`.

## Connect

```bash
claude mcp add --scope user tokensaver -- tokensaver
```

Cursor, Claude Desktop, other MCP clients — add this server and restart:

```json
{ "mcpServers": { "tokensaver": { "command": "tokensaver" } } }
```

## Use

You don't call it yourself — just ask your agent:

```text
read https://go.dev/doc/effective_go with tokensaver
outline https://arxiv.org/pdf/1706.03762 with tokensaver, then read just the Attention section
read https://github.com/use-tokensaver/tokensaver/pull/16 with tokensaver
fetch https://api.github.com/search/repositories?q=language:go with tokensaver — just full_name and stargazers_count, as a table
```

Reads: web pages, PDF, DOCX, XLSX, PPTX, JSON, diffs and PRs, ZIP, log files, folders,
and any text file.

## How much it saves

Measured on real sources (tokens ≈ characters ÷ 4; reproduce with
`TOKENSAVER_LIVE=1 go test ./e2e/ -run Live -v`):

| Source | Raw tokens | With tokensaver | Saved |
|---|---:|---:|---:|
| Wikipedia article | 183,202 | 19,383 | 89% |
| …just its outline | | 248 | 99.9% |
| GitHub repo page | 87,100 | 1,433 | 98% |
| GitHub API, 50 repos, picked fields as a table | 78,745 | 379 | 99.5% |
| Log file, 401 lines, 2 incidents (offline test) | 5,315 | 135 | 97.5% |

## Learn more

[Docs](https://use-tokensaver.github.io/tokensaver/docs/) — every option, configuration,
telemetry and security notes. Developing it? `go test ./...`, and see
[CLAUDE.md](CLAUDE.md) for the layout and release flow.

MIT licensed — see [LICENSE](LICENSE).
