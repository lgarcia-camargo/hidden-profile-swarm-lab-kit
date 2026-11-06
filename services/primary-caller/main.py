#!/usr/bin/env python3
"""Run Primary Caller API (uvicorn)."""
from __future__ import annotations

import uvicorn

from primary_caller.config import DEFAULT_HOST, DEFAULT_PORT


def main() -> None:
    uvicorn.run(
        "primary_caller.api:app",
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        reload=False,
    )


if __name__ == "__main__":
    main()
