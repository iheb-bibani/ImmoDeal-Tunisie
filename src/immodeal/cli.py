import argparse

from .collectors.tayara import TayaraCollector
from .raw.archive import RawArchive, SnapshotCollisionError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("immodeal")
    sub = parser.add_subparsers(dest="cmd", required=True)
    tayara = sub.add_parser("collect-tayara", help="Archive raw public Tayara real-estate listings")
    tayara.add_argument("--db", default="data/raw_metadata.db")
    tayara.add_argument("--payload-root", default="data/raw_payloads")
    tayara.add_argument("--limit", type=int, default=100)
    tayara.add_argument("--pages", type=int, default=1)
    tayara.add_argument("--delay", type=float, default=1.5)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.cmd != "collect-tayara":
        return

    archive = RawArchive(args.db, args.payload_root)
    try:
        collector = TayaraCollector(delay_seconds=args.delay)
        candidates = collector.discover_pages(max_pages=args.pages)
        if args.limit > 0:
            candidates = candidates[: args.limit]
        stats = {"discovered": len(candidates), "archived": 0, "collisions": 0, "failed": 0}
        for candidate in candidates:
            try:
                archive.ingest(collector.fetch(candidate))
                stats["archived"] += 1
            except SnapshotCollisionError:
                stats["collisions"] += 1
            except Exception as exc:
                stats["failed"] += 1
                print(f"ERROR {candidate.url}: {exc}")
        print(stats)
    finally:
        archive.close()


if __name__ == "__main__":
    main()
