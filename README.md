# SSE Media Player

Run a small Python service that listens to an SSE stream and plays media files from `/workspace/media`. When a new file is requested and exists, the current playback is stopped (if any) and the new file starts.

## Requirements

- Python 3.10+
- `ffplay` from FFmpeg installed and in `PATH`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Environment variables (optional):

- `SSE_URL`: SSE endpoint. Default `http://localhost:8000/stream`.
- `MEDIA_DIR`: Directory containing media files. Default `/workspace/media`.
- `PLAYER_CMD`: Player command. Default `ffplay -autoexit -nodisp -loglevel error`.

You can place these in a `.env` file at repo root.

## Run

```bash
python sse_player.py
```

SSE events should contain a file path (absolute or relative to `MEDIA_DIR`). 
