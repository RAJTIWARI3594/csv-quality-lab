# CSV Quality Lab

Profile CSV files, reject malformed rows, report duplicate/blank/type issues and export a conservative whitespace-cleaned copy with an audit report.

## Quick start

```sh
python quality.py sample/orders.csv --key order_id --out report.json --clean cleaned.csv
```

## Tests

`python -m unittest discover -s tests -v`

## Scope and limitations

Local CSV tool, maximum 10 MB / 100,000 rows. It never invents missing values, silently removes duplicates or overwrites inputs. Values beginning with spreadsheet formula characters are flagged; optional `--spreadsheet-safe` prefixes them in the exported copy. Inferred types are descriptive, not business validation.

## Attribution and sample data

Built for Raj's portfolio with Wabi AI assistance. Sample data is invented and labelled synthetic; no real customer, employer or private account records are included. This is a learning/portfolio implementation, not a claim of commercial work or production deployment.

See source and tests for implementation decisions. Use invented data when exploring.

## How it works

CSV bytes → strict parser → per-column profile → JSON audit + explicit CSV export. Analysis leaves source bytes unchanged; malformed row widths abort instead of silently truncating data.

## Verified example

Sample: 4 rows, one repeated order ID; whitespace trimmed and formula-like exported values prefixed only with --spreadsheet-safe.

See [VALIDATION.md](VALIDATION.md) for tested environments and scope.
