import streamlit as st
import os
import tkinter as tk
from tkinter import filedialog
import converter
import tifffile

# Page Setup
st.set_page_config(page_title="3D Tif to AmiraMesh Converter", layout="centered")

# Custom CSS for aesthetics
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4CAF50; 
        color: white;
    }
    .main {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

def select_file_dialog():
    """Opens a native file selection dialog."""
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        file_path = filedialog.askopenfilename(
            title="Select 3D Tif File",
            filetypes=[("Tif files", "*.tif;*.tiff")],
            initialdir=os.getcwd()
        )
        root.destroy()
        return file_path
    except Exception as e:
        st.error(f"Failed to open file dialog: {e}")
        return None

def save_file_dialog(default_name):
    """Opens a native save file dialog."""
    try:
        root = tk.Tk()
        root.withdraw()
        root.wm_attributes('-topmost', 1)
        file_path = filedialog.asksaveasfilename(
            title="Save AmiraMesh File",
            initialdir=os.getcwd(),
            initialfile=default_name,
            defaultextension=".am",
            filetypes=[("AmiraMesh files", "*.am")]
        )
        root.destroy()
        return file_path
    except Exception as e:
        st.error(f"Failed to open save dialog: {e}")
        return None

# Title
st.title("3D Tif to AmiraMesh Converter")
st.markdown("Convert 3D Tiff stacks to AmiraMesh ASCII 2.0 format.")

# Session State Initialization
if 'selected_file' not in st.session_state:
    st.session_state['selected_file'] = None
if 'file_meta' not in st.session_state:
    st.session_state['file_meta'] = {}

# Step 1: File Selection
st.header("1. File Selection")
if st.button("Browse 3D Tif File"):
    path = select_file_dialog()
    if path:
        st.session_state['selected_file'] = path
        # Read metadata for preview (avoid full load if possible, but converter.read_tif does full load)
        # Using tifffile directly for lightweight check
        try:
            with tifffile.TiffFile(path) as tif:
                st.session_state['file_meta'] = {
                    'shape': tif.series[0].shape, # (z, y, x) usually
                    'dtype': str(tif.series[0].dtype)
                }
        except Exception as e:
            st.error(f"Error reading file info: {e}")

# Step 2: Confirmation & Settings
if st.session_state['selected_file']:
    file_path = st.session_state['selected_file']
    meta = st.session_state['file_meta']
    
    st.divider()
    st.header("2. Settings & Confirmation")
    
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.write(f"**Filename:** `{os.path.basename(file_path)}`")
    with col_info2:
        st.write(f"**Dimensions (Z, Y, X):** `{meta.get('shape', 'Unknown')}`")
    
    st.subheader("Voxel Size")
    st.caption("Enter voxel size in desired units (e.g., nm, um).")
    
    c1, c2, c3 = st.columns(3)
    vx = c1.number_input("X Size", min_value=0.0, value=1.0, format="%.4f")
    vy = c2.number_input("Y Size", min_value=0.0, value=1.0, format="%.4f")
    vz = c3.number_input("Z Size", min_value=0.0, value=1.0, format="%.4f")
    
    st.divider()
    
    # Step 3: Convert
    if st.button("Convert to AmiraMesh"):
        default_out = os.path.basename(file_path).rsplit('.', 1)[0] + "-3d-ascii.am"
        save_path = save_file_dialog(default_out)
        
        if save_path:
            progress_bar = st.progress(0, text="Reading Tif file...")
            
            try:
                # 1. Read
                data, _ = converter.read_tif(file_path)
                progress_bar.progress(30, text="Processing data...")
                
                # 2. Write
                progress_bar.progress(50, text="Writing AmiraMesh file (this may take a while)...")
                converter.write_amira(save_path, data, (vx, vy, vz))
                
                progress_bar.progress(100, text="Done!")
                st.success(f"Conversion Complete! Saved to: `{save_path}`")
                
                # Optional: Show path in explorer?
                # st.button("Open Output Folder") ...
                
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
            finally:
                pass
