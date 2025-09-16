#!/usr/bin/env python3
import os
import subprocess
import sys
import time
from pathlib import Path

import psutil
from dotenv import load_dotenv
from sseclient import SSEClient


load_dotenv(override=False)
MEDIA_DIR = Path(os.getenv("MEDIA_DIR", "/workspace/media")).expanduser().resolve()
SSE_URL = os.getenv("SSE_URL", "http://localhost:8000/stream")
PLAYER_CMD = os.getenv("PLAYER_CMD", "ffplay -autoexit -nodisp -loglevel error").split()


class MediaPlayerManager:
	def __init__(self) -> None:
		self.current_process: psutil.Process | None = None

	def is_playing(self) -> bool:
		return self.current_process is not None and self.current_process.is_running() and self.current_process.status() != psutil.STATUS_ZOMBIE

	def stop(self) -> None:
		if not self.is_playing():
			self.current_process = None
			return
		try:
			proc = self.current_process
			assert proc is not None
			for child in proc.children(recursive=True):
				child.terminate()
			proc.terminate()
			_, alive = psutil.wait_procs([proc], timeout=3)
			for p in alive:
				p.kill()
		except Exception:
			pass
		finally:
			self.current_process = None

	def play(self, media_path: Path) -> None:
		self.stop()
		cmd = PLAYER_CMD + [str(media_path)]
		process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, preexec_fn=os.setsid)
		self.current_process = psutil.Process(process.pid)


def ensure_media_dir() -> None:
	MEDIA_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
	ensure_media_dir()
	player = MediaPlayerManager()
	print(f"Connecting to SSE server: {SSE_URL}")
	while True:
		try:
			client = SSEClient(SSE_URL, retry=3000)
			for event in client.events():
				if not event.data:
					continue
				path = event.data.strip()
				candidate = (MEDIA_DIR / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
				if not candidate.exists():
					print(f"[skip] File not found: {candidate}")
					continue
				if player.is_playing():
					print("Stopping current playback...")
				player.play(candidate)
				print(f"Playing: {candidate}")
		except KeyboardInterrupt:
			print("Interrupted. Exiting.")
			player.stop()
			return 0
		except Exception as exc:
			print(f"SSE connection error: {exc}. Reconnecting in 3s...", file=sys.stderr)
			time.sleep(3)


if __name__ == "__main__":
	sys.exit(main())