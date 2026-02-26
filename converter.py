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

def write_amira(output_path, data, voxel_size_nm, ascii_format=True):
    """
    Writes numpy data to AmiraMesh 3D ASCII 2.0 or BINARY format.
    
    Args:
        output_path (str): Path to save .am file.
        data (numpy.ndarray): 3D data array (z, y, x).
        voxel_size_nm (tuple): (vx, vy, vz) in physical units.
        ascii_format (bool): Write in ASCII format if True, else Binary.
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
        
        dtype_map = {
            'uint8': 'byte',
            'int8': 'char',
            'uint16': 'ushort',
            'int16': 'short',
            'uint32': 'int', 
            'int32': 'int',
            'float32': 'float',
            'float64': 'double'
        }
        
        numpy_type = str(data.dtype)
        amira_type = dtype_map.get(numpy_type, 'float') # Default to float if unknown
        
        mode = 'w' if ascii_format else 'wb'
        encoding = 'utf-8' if ascii_format else None
        
        with open(output_path, mode, encoding=encoding) as f:
            header = ""
            if ascii_format:
                header += "# AmiraMesh 3D ASCII 2.0\n\n"
            else:
                header += "# AmiraMesh BINARY-LITTLE-ENDIAN 2.1\n\n"
            
            header += f"define Lattice {nx} {ny} {nz}\n\n"
            header += "Parameters {\n"
            header += "    Content \"Calculated by Tif2AM\",\n"
            header += f"    BoundingBox {x_min} {x_max} {y_min} {y_max} {z_min} {z_max},\n"
            header += "    CoordType \"uniform\"\n"
            header += "}\n\n"
            header += f"Lattice {{ {amira_type} Data }} @1\n\n"
            header += "# Data section follows\n"
            header += "@1\n"
            
            if ascii_format:
                f.write(header)
                flat_data = data.flatten()
                
                chunk_size = 100000
                for i in range(0, len(flat_data), chunk_size):
                    chunk = flat_data[i:i+chunk_size]
                    chunk_str = '\n'.join([str(val) for val in chunk])
                    f.write(chunk_str)
                    f.write("\n")
            else:
                f.write(header.encode('ascii'))
                
                # Ensure data is little endian for the binary write
                if data.dtype.byteorder == '>':
                    data = data.byteswap().newbyteorder()
                elif data.dtype.byteorder == '=':
                    import sys
                    if sys.byteorder == 'big':
                        data = data.byteswap().newbyteorder()
                        
                # write binary data efficiently (C-order traversal is default, meaning x varies fastest)
                data.tofile(f)
                
    except Exception as e:
         raise RuntimeError(f"Failed to write Amira file: {e}")

