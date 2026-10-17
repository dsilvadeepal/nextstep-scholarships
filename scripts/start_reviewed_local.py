"""Start the local reviewed-corpus demo using the retained $5 cumulative ledger."""

import uvicorn
from nextstep.app import create_app
from reviewed_runtime import live_settings

if __name__ == "__main__":
    uvicorn.run(create_app(live_settings()), host="127.0.0.1", port=8014)
