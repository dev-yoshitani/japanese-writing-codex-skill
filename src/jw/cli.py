import argparse
import json
import sys
from pathlib import Path
from . import __version__
from .adapters import ReplayAdapter
from .config import load_data
from .core.constraints import Constraints, GENRES
from .core.report import compare, summary
from .pipeline import run


def _read(path):
    if path == "-":
        return sys.stdin.read()
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return handle.read()


def _write_new(path, text, input_paths):
    destination = Path(path).resolve()
    if destination in {Path(p).resolve() for p in input_paths if p != "-"}:
        raise ValueError("Output must differ from all input paths")
    # Explicit paths only, exclusive creation, no overwrite flag. No path is ever
    # taken from model output; ordinary absolute user paths are supported.
    with destination.open("x", encoding="utf-8", newline="") as handle:
        handle.write(text)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="jw", description="Lexical verification for Japanese revisions; not semantic proof")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("audit", "compare", "replay"):
        command = commands.add_parser(name)
        command.add_argument("source")
        if name == "compare":
            command.add_argument("target")
        if name == "replay":
            command.add_argument("responses", help="JSON array of explicit replay responses")
            command.add_argument("--max-revision", type=int, default=2)
            command.add_argument("--output", required=True, help="New file for accepted prose; never overwritten")
        command.add_argument("--genre", choices=GENRES)
        command.add_argument("--json", action="store_true", dest="as_json")
        command.add_argument("--report", help="Explicit new report file; defaults to stdout")
        command.add_argument("--config", help="Explicit JSON / flat YAML configuration")
        command.add_argument("--glossary", help="JSON / flat YAML with a terms list")
        command.add_argument("--min-chars", type=int)
        command.add_argument("--max-chars", type=int)
        command.add_argument("--count-mode", choices=("all", "no_newlines", "no_whitespace"))
        command.add_argument("--require", action="append")
        command.add_argument("--forbid", action="append")
        command.add_argument("--max-edit-ratio", type=float)
        command.add_argument("--strictness", choices=("conservative", "balanced", "broad"), help="Opt-in edit limits: 0.15 / 0.35 / 0.65")
        command.add_argument("--include-values", action="store_true", help="Explicitly include protected values in the report")
    args = parser.parse_args(argv)
    try:
        config = load_data(args.config) if args.config else {}
        accepted_keys = {"min_chars", "max_chars", "count_mode", "required", "forbidden", "max_edit_ratio", "genre", "terms"}
        if config.keys() - accepted_keys:
            raise ValueError("Unknown configuration keys")
        terms = config.pop("terms", [])
        if not isinstance(terms, list):
            raise ValueError("terms must be a list")
        if args.glossary:
            glossary = load_data(args.glossary)
            if set(glossary) != {"terms"} or not isinstance(glossary["terms"], list):
                raise ValueError("Glossary requires exactly a terms list")
            terms = terms + glossary["terms"]
        if any(not isinstance(t, str) or not t.strip() for t in terms):
            raise ValueError("terms must contain nonempty strings")
        genre = args.genre or config.pop("genre", "natural")
        config.pop("genre", None)
        for attr in ("min_chars", "max_chars", "count_mode", "max_edit_ratio"):
            value = getattr(args, attr)
            if value is not None:
                config[attr] = value
        if args.strictness and args.max_edit_ratio is None:
            config["max_edit_ratio"] = {"conservative": 0.15, "balanced": 0.35, "broad": 0.65}[args.strictness]
        for attr, option in (("required", args.require), ("forbidden", args.forbid)):
            if option is not None:
                config[attr] = option
        constraints = Constraints(**config)
        source = _read(args.source)
        inputs = [args.source, *[p for p in (args.config, args.glossary) if p]]
        if args.command == "replay":
            inputs.append(args.responses)
            responses = json.loads(_read(args.responses))
            if not isinstance(responses, list):
                raise ValueError("Replay file must contain an array")
            # Validate output destinations before doing any writes.
            destinations = [args.output] + ([args.report] if args.report else [])
            if len({Path(p).resolve() for p in destinations}) != len(destinations):
                raise ValueError("Prose and report destinations must differ")
            for path in destinations:
                if Path(path).exists() or Path(path).resolve() in {Path(p).resolve() for p in inputs if p != "-"}:
                    raise ValueError("Output destination already exists or aliases an input")
            state = run(source, ReplayAdapter(responses), terms=terms, constraints=constraints, genre=genre, max_revision=args.max_revision)
            report = state.report
            if state.output is not None:
                _write_new(args.output, state.output, inputs)
        else:
            if args.command == "compare" and args.source == args.target == "-":
                raise ValueError("Only one input may use stdin")
            target = _read(args.target) if args.command == "compare" else None
            if args.command == "compare":
                inputs.append(args.target)
            report = compare(source, target, terms=terms, constraints=constraints, genre=genre, include_values=args.include_values)
        rendered = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) if args.as_json else summary(report)
        if args.report:
            _write_new(args.report, rendered + "\n", inputs)
        else:
            print(rendered)
        return 1 if report["status"] == "FAIL" else 0
    except (ValueError, OSError, TypeError, KeyError):
        # Parsing and IO exception messages can contain private input or paths.
        print("jw: invalid input, configuration, contract, or output path; no overwrite permitted", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
