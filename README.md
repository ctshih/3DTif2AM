# 3D Tif 轉 AmiraMesh 轉換器

這是一個簡單的 Python 工具，用於將 3D Tiff 影像轉換為 AmiraMesh 3D ASCII 2.0 格式。

## 功能
- **圖形介面**：基於 Streamlit 的瀏覽器介面。
- **原生檔案視窗**：使用標準 Windows 對話方塊選擇檔案與儲存路徑。
- **自訂 Voxel 尺寸**：可輸入 X、Y、Z 方向的 Voxel 大小（例如：nm 或微米）。
- **自動偵測**：自動偵測 3D 檔案並顯示尺寸資訊。

## 系統需求
- Python 3.8+
- `streamlit`
- `tifffile`
- `numpy`

## 安裝
相依套件應會自動安裝。若沒有，請執行：
```bash
pip install -r requirements.txt
```

##以此執行
雙擊 `run_app.bat` 或執行以下指令：
```bash
python -m streamlit run app.py
```

## 使用方法
1. 點擊 **Browse 3D Tif File** 按鈕。
2. 從跳出的視窗中選取您的 `.tif` 檔案。
3. 確認顯示的檔案尺寸是否正確。
4. 輸入 X、Y、Z 的 **Voxel Size**。
5. 點擊 **Convert to AmiraMesh** 按鈕。
6. 選擇 `.am` 檔案的儲存位置。
7. 等待顯示「Conversion Complete」訊息即完成。
