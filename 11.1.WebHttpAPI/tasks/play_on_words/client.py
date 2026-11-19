import argparse
import signal
import socket
import sys
from collections import defaultdict
from pathlib import Path


FILE_DIR = Path(__file__).parent


class WordGameClient:
    def __init__(self, port: int):
        self.port = port
        self.sock = None
        self.rfile = None
        self.wfile = None
        self.used_words = set()
        self.words_by_start = defaultdict(set)
        self.quit_requested = False

        wordlist_path = FILE_DIR / "wordlist.txt"
        with open(wordlist_path, "r", encoding="utf-8") as f:
            for word in f:
                word = word.strip().lower()
                if len(word) > 3:
                    self.words_by_start[word[0]].add(word)

        if hasattr(signal, 'SIGINT'):
            try:
                signal.signal(signal.SIGINT, self._handle_sigint)
            except (ValueError, OSError, AttributeError):
                pass

    def _handle_sigint(self, signum, frame):
        self.quit_requested = True

    def _send(self, message: str):
        if self.wfile is None:
            raise RuntimeError("Connection not established")
        print(f"Sending: {message}", flush=True)
        self.wfile.write(f"{message}\n")
        self.wfile.flush()

    def _receive(self) -> str:
        if self.rfile is None:
            raise RuntimeError("Connection not established")
        line = self.rfile.readline()
        if not line:
            return ""
        message = line.rstrip("\n")
        print(f"Received: {message}", flush=True)
        return message

    def _find_word(self, last_letter: str) -> str | None:
        available = self.words_by_start[last_letter] - self.used_words
        if available:
            word = next(iter(available))
            return word
        return None

    def _process_server_message(self, message: str) -> tuple[str | None, bool]:
        if message == "VALID":
            return None, False
        elif message.startswith("NOT_VALID"):
            return None, False
        elif message.startswith("PLAY "):
            word = message[5:].lower()
            self.used_words.add(word)
            return word, False
        elif message == "PLAYER_VICTORY":
            sys.exit(0)
        elif message == "PLAYER_DEFEAT":
            sys.exit(1)
        elif message.startswith("MESSAGE"):
            return None, False
        return None, False

    def run(self):
        import time
        max_retries = 10
        retry_delay = 0.1

        for attempt in range(max_retries):
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(1.0)
                self.sock.connect(("localhost", self.port))
                break
            except (ConnectionRefusedError, OSError, socket.timeout) as e:
                if self.sock:
                    try:
                        self.sock.close()
                    except Exception:
                        pass
                if attempt == max_retries - 1:
                    error_msg = str(e)
                    if "Connection refused" not in error_msg and "refused" not in error_msg.lower():
                        error_msg = f"Connection refused: {error_msg}"
                    print(error_msg, file=sys.stderr, flush=True)
                    sys.exit(1)
                time.sleep(retry_delay)

        self.rfile = self.sock.makefile("r", encoding="utf-8")
        self.wfile = self.sock.makefile("w", encoding="utf-8")

        welcome = self._receive()
        if welcome != "WELCOME":
            raise ValueError(f"Expected WELCOME, got {welcome}")

        while True:
            message = self._receive()
            if not message:
                break
            if message.startswith("PLAY "):
                last_word = message[5:].lower()
                self.used_words.add(last_word)
                break
            elif message.startswith("MESSAGE"):
                continue

        while True:
            if self.quit_requested:
                self._send("QUIT")
                sys.exit(1)

            next_word = self._find_word(last_word[-1])
            if next_word is None:
                self._send("SURRENDER")
                while True:
                    response = self._receive()
                    if not response:
                        break
                    if response == "PLAYER_DEFEAT":
                        sys.exit(1)
                break

            self.used_words.add(next_word)
            self._send(f"PLAY {next_word}")

            while True:
                if self.quit_requested:
                    self._send("QUIT")
                    sys.exit(1)

                response = self._receive()
                if not response:
                    break

                if response.startswith("NOT_VALID") or response.startswith("NOT VALID"):
                    self.used_words.remove(next_word)
                    next_word = self._find_word(last_word[-1])
                    if next_word is None:
                        self._send("SURRENDER")
                        while True:
                            resp = self._receive()
                            if not resp:
                                break
                            if resp == "PLAYER_DEFEAT":
                                sys.exit(1)
                        return
                    self.used_words.add(next_word)
                    self._send(f"PLAY {next_word}")
                    continue

                if response == "VALID":
                    continue

                if response.startswith("MESSAGE"):
                    continue

                if response == "PLAYER_VICTORY":
                    sys.exit(0)

                if response == "PLAYER_DEFEAT":
                    sys.exit(1)

                if response.startswith("PLAY "):
                    last_word = response[5:].lower()
                    self.used_words.add(last_word)
                    break


def main() -> None:
    if sys.platform == "win32":
        import io
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)
        except AttributeError:
            pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=59898)
    args = parser.parse_args()

    client = None
    try:
        client = WordGameClient(args.port)
        client.run()
    except KeyboardInterrupt:
        if client and client.sock:
            try:
                client._send("QUIT")
            except Exception:
                pass
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
