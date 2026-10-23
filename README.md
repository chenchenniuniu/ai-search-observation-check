# AI search observation check

A small, dependency-free Python 3.10+ validator for exported AI-search observations. It keeps collection failures separate from observed brand absence. It does not query AI services, collect credentials, or estimate rankings.

## Run

```sh
python3 check.py example.jsonl
python3 -m unittest -v
```

The **synthetic** example contains two completed observations (one mention and one absence) plus one timeout. Its observed mention rate is 1/2; its completion fraction is 2/3. Counting the timeout as an absence would incorrectly report 1/3.

## Record contract

Each nonblank JSONL line is an object with nonempty strings `id`, `engine`, `language`, `prompt_id`, and a timezone-aware ISO timestamp `observed_at`.

`status` is one of `completed`, `failed`, `timeout`, or `skipped`. A completed record requires a JSON boolean `brand_mentioned`. Other statuses must omit that field or set it to `null`. Duplicate record IDs fail validation. Errors include a line number and exit with code 2.

Use distinct IDs for separate observations. Multiple legitimate observations of one prompt are allowed; the tool does not infer sampling weights or independence. A completed observation must reflect your own checked data, not a fabricated response or an HTTP success alone.

## Interpret the output

- `observed_mention_rate` uses only completed observations as its denominator.
- An empty dataset or a dataset with no completed observations produces `null`, meaning unknown.
- `completion_fraction` shows data availability separately. It includes skipped records in its denominator, so document your scheduling scope.
- These are descriptive results for the supplied sample. They are not population visibility, causal lift, statistical significance, conversion attribution, or a ranking guarantee.

Raw prompts, customer names and response text are deliberately unnecessary. Use nonsensitive prompt IDs and export only data you are allowed to share. No customer or production data is included here.

Prepared as a technical resource for [GeoEcho](https://geoecho.ai/). The implementation and documentation were created with AI assistance. This resource makes no independent claim about GeoEcho performance, supported engines, customer results or pricing.

## License

MIT. See `LICENSE`. This is an educational reference implementation, not an official schema for any AI provider.
