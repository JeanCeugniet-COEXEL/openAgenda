#!/usr/bin/env python3
import uvicorn

if __name__ == "__main__":
    uvicorn.run("mytwip.api.openagenda.app:app", host="0.0.0.0", port=9000, reload=True)