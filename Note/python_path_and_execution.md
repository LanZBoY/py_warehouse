# Technical Note: Python Path and Project Execution

## 1. 模組尋找機制 (Module Discovery)
在目前的專案架構中，所有導入語句都使用絕對路徑（例如 `from src.app.core...`）。這依賴於 Python 的 `sys.path`。

*   **執行路徑 (CWD)**：當你在根目錄執行指令時，該目錄會自動加入 `sys.path`。
*   **src 佈局**：這是一種常見的 Python 專案佈局，確保程式碼不會意外地被導入，除非明確指定。

## 2. 為什麼 `src/app/main.py` 能找到根目錄？
這是基於 **Execution Path (執行路徑)**。
*   指令：`uv run uvicorn src.app.main:app`
*   此時 CWD 是專案根目錄，Python 引擎看到 `src` 資料夾，因此 `from src.app...` 能夠成功解析。
*   **警告**：如果你進入 `src/app` 並執行 `uvicorn main:app`，則會發生 `ModuleNotFoundError`，因為 Python 找不到名為 `src` 的模組。

## 3. 環境變數 (.env) 的讀取
`pydantic-settings` 預設也會從 **CWD** 尋找 `.env` 檔案。
*   如果你在根目錄啟動，它能找到 `.env`。
*   這也是為什麼我們不需要在程式碼中寫死 `.env` 的絕對路徑。

## 4. 最佳實踐建議
1.  **統一執行入口**：永遠在專案根目錄執行指令（或透過 Makefile/Task Runner 封裝）。
2.  **避免相對導入**：在大型 DDD 專案中，使用絕對路徑（從 `src` 開始）能讓重構更安全且結構更清晰。
3.  **Docker 部署**：在 Dockerfile 中，設定 `WORKDIR /app` 並將內容拷貝至此，確保執行環境與開發環境一致。
