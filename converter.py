import tifffile
import numpy as np
import os

def read_tif(file_path):
    """
    Reads a 3D Tif file.
    Returns:
        data (numpy.ndarray): The 3D image data.
        metadata (dict): Basic metadata (shape, dtype).
    """
    try:
        data = tifffile.imread(file_path)
        # Ensure it's 3D
        if data.ndim == 2:
            # If 2D, maybe just one slice, expand dims? Or raise error?
            # User specified "3D Tif file", so we assume stack or multi-page.
            # If single page 2D, we treat as 1 slice 3D.
            data = data[np.newaxis, :, :]
        
        metadata = {
            'shape': data.shape, # (z, y, x)
            'dtype': str(data.dtype),
            'min': float(data.min()),
            'max': float(data.max())
        }
        return data, metadata
    except Exception as e:
        raise RuntimeError(f"Failed to read Tif file: {e}")

def write_amira(output_path, data, voxel_size_nm):
    """
    Writes numpy data to AmiraMesh 3D ASCII 2.0 format.
    
    Args:
        output_path (str): Path to save .am file.
        data (numpy.ndarray): 3D data array (z, y, x).
        voxel_size_nm (tuple): (vx, vy, vz) in physical units.
    """
    try:
        # Data shape is (z, y, x)
        nz, ny, nx = data.shape
        vx, vy, vz = voxel_size_nm
        
        # Calculate Bounding Box
        # Amira BoundingBox xmin xmax ymin ymax zmin zmax
        x_min, x_max = 0.0, nx * vx
        y_min, y_max = 0.0, ny * vy
        z_min, z_max = 0.0, nz * vz
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write("# AmiraMesh 3D ASCII 2.0\n\n")
            
            # Lattice definition
            f.write(f"define Lattice {nx} {ny} {nz}\n\n")
            
            # Parameters
            f.write("Parameters {\n")
            f.write("    Content \"Calculated by Tif2AM\",\n")
            f.write(f"    BoundingBox {x_min} {x_max} {y_min} {y_max} {z_min} {z_max},\n")
            f.write("    CoordType \"uniform\"\n")
            f.write("}\n\n")
            
            # Data section definition
            # Determine Amira type from numpy type
            # Common types: byte, short, ushort, int, float, double
            dtype_map = {
                'uint8': 'byte',
                'int8': 'char',
                'uint16': 'ushort',
                'int16': 'short',
                'uint32': 'int', # Amira 'int' is 32-bit signed usually, but 'uint' exists? check spec. 
                                # AmiraMesh ASCII 2.0 often uses 'byte', 'short', 'float'.
                                # Let's convert to standard acceptable types if needed.
                'int32': 'int',
                'float32': 'float',
                'float64': 'double'
            }
            
            # Amira 'byte' is unsigned 8-bit usually in binary, but in ASCII it's just numbers.
            # But the declaration matters.
            # 'byte' 0-255.
            
            numpy_type = str(data.dtype)
            amira_type = dtype_map.get(numpy_type, 'float') # Default to float if unknown
            
            f.write(f"Lattice {{ {amira_type} Data }} @1\n\n")
            f.write("# Data section follows\n")
            f.write("@1\n")
            
            # Writing ASCII data
            # Data should be written such that x varies fastest
            # data is (z, y, x). data.flatten() does (z, y, x) -> z0y0x0, z0y0x1...
            # corresponding to Lattice {nx} {ny} {nz} where x is first dim?
            # Wait, "define Lattice nx ny nz". 
            # In Amira, indices are i, j, k corresponding to x, y, z.
            # Access is usually (x + y*nx + z*nx*ny).
            # So x is fastest.
            # Numpy (row-major C) flatten on shape (z, y, x) traverses last index (x) fastest.
            # So data.flatten() is correct for "x varies fastest".
            
            # Using savetxt on flattened array might be memory intensive but easy for implementation.
            # For 120MB Uint8 -> 120M integers.
            # 120 * 1024*1024 points.
            # Writing line by line or chunking is better.
            
            flat_data = data.flatten()
            
            # Write in chunks to avoid massive string construction
            # But ASCII needs spaces/newlines.
            # np.savetxt is good but can't append easily without reopen?
            # Actually we can iterate.
            
            # Fast ASCII write
            # tofile is binary.
            # savetxt handles 1D or 2D.
            
            # Check size, if too big, might warn user.
            # For this task, we assume it fits in memory (user has 3D tiff).
            
            # A simple way to write large list of numbers:
            # Chunking
            chunk_size = 100000
            for i in range(0, len(flat_data), chunk_size):
                chunk = flat_data[i:i+chunk_size]
                # Convert to string
                # ' '.join(map(str, chunk)) is standard but slowish.
                # data.tofile(sep=" ") ??
                # numpy.ndarray.tofile(fid, sep="", format="%s") 
                # This writes to a file object if sep is used (text mode)? 
                # Doc says: "sep : str. Separator between array items for text output. If “” (empty), a binary file is written, equivalent to file.write(a.tobytes())."
                # "file : file or str"
                
                # So we can use tofile with file HANDLE if we flush?
                # Actually .tofile takes a file PATH or file Object.
                # Note: tofile with file *object* only works in some numpy versions/configs? 
                # Let's try tofile logic by opening file in append mode?
                # But we already have 'f' open.
                
                # Actually, plain old f.write with string join of chunks
                chunk_str = '\n'.join([str(val) for val in chunk]) # Newline separated is fine for Amira ASCII? 
                # Amira ASCII can be space or newline separated.
                f.write(chunk_str)
                f.write("\n")
                
    except Exception as e:
         raise RuntimeError(f"Failed to write Amira file: {e}")

