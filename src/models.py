from dataclasses import dataclass


@dataclass
class LWWDocument:
    doc_id: str
    content: str
    timestamp: float  # server timestamp of last write

    def save_edit(self, new_content: str, server_timestamp: float, origin: str) -> str:
        """
        LWW: blindly accept the write if its timestamp is newer.
        Clock skew means 'newer' is unreliable.
        """
        if server_timestamp > self.timestamp:
            old = self.content
            self.content = new_content
            self.timestamp = server_timestamp
            print(
                f"  [{origin}] ACCEPTED  | ts={server_timestamp}ms | '{old}' → '{self.content}'"
            )
            return "saved"
        else:
            print(
                f"  [{origin}] REJECTED  | ts={server_timestamp}ms < current={self.timestamp}ms "
                f"| '{new_content}' discarded"
            )
            return "conflict: newer version exists"
