from src.models import LWWDocument
from src.server import Operation, OTServer


def divider(title: str):
    width = 60
    print(f"\n{'─' * width}")
    print(f"  {title}")
    print(f"{'─' * width}")


def simulate_lww():
    divider("PART 1 — Last Write Wins (the broken architecture)")

    # Sydney's server clock is 50ms behind real time
    US_CLOCK_OFFSET = 0
    SYDNEY_CLOCK_OFFSET = -50  # skewed

    real_time_us_writes = 1000  # US writes at real T=1000ms
    real_time_sydney_writes = 1020  # Sydney writes AFTER at real T=1020ms

    us_server_ts = real_time_us_writes + US_CLOCK_OFFSET  # 1000ms
    sydney_server_ts = real_time_sydney_writes + SYDNEY_CLOCK_OFFSET  # 970ms

    print("\n  Initial document: 'Hello World'")
    print("\n  Clock state:")
    print(f"    US server timestamp   : {us_server_ts}ms")
    print(f"    Sydney server timestamp: {sydney_server_ts}ms (50ms skewed)")
    print("\n  Both users read 'Hello World' concurrently.")
    print("  US user inserts ' beautiful' → 'Hello beautiful World'")
    print("  Sydney user (AFTER seeing US edit) appends '!' → 'Hello beautiful World!'")
    print("\n  Writes:")

    doc = LWWDocument(doc_id="doc-1", content="Hello World", timestamp=0.0)

    # US writes first (physically and by clock)
    doc.save_edit("Hello beautiful World", us_server_ts, "US")

    # Sydney writes after in real time, but its clock says earlier
    doc.save_edit("Hello beautiful World!", sydney_server_ts, "Sydney")

    print(f"\n  Final document : '{doc.content}'")
    print("  Expected       : 'Hello beautiful World!'")
    print(
        f"  Data lost      : {'YES — Sydney edit silently discarded' if doc.content != 'Hello beautiful World!' else 'No'}"
    )


def simulate_ot():
    divider("PART 2 — Operational Transformation (the fix)")

    print("\n  Initial document: 'Hello World'")
    print("\n  Concurrent ops (both based on 'Hello World'):")
    print("    US     : insert(' beautiful', pos=5)  → 'Hello beautiful World'")
    print("    Sydney : insert('!', pos=11)           → 'Hello World!'")
    print(
        "\n  Without transformation, applying both would give: 'Hello beautiful Wor!ld'"
    )
    print("  With OT, Sydney's position is adjusted after US's insert.")
    print("\n  Processing:")

    server = OTServer(doc_id="doc-1", content="Hello World")

    # Both ops are based on the original document at T=0
    # Timestamps reflect when each op was GENERATED, not wall-clock order
    us_op = Operation(
        type="insert", position=5, char=" beautiful", timestamp=0, origin="US"
    )
    sydney_op = Operation(
        type="insert", position=11, char="!", timestamp=0, origin="Sydney"
    )

    # US op arrives first — no concurrent ops to transform against yet
    server.apply(us_op)

    # Sydney op arrives — must be transformed against US op
    server.apply(sydney_op)

    print(f"\n  Final document : '{server.content}'")
    print("  Expected       : 'Hello beautiful World!'")
    print(
        f"  Data lost      : {'YES' if server.content != 'Hello beautiful World!' else 'No — both edits preserved'}"
    )


# ─────────────────────────────────────────────
# ─────────────────────────────────────────────

if __name__ == "__main__":
    simulate_lww()
    simulate_ot()
    print(f"\n{'─' * 60}\n")
