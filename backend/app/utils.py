"""
Utility functions for API responses and data handling
"""

import json
import numpy as np
import torch
from datetime import datetime
from decimal import Decimal


class NumpyTorchEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy and torch types"""
    
    def default(self, obj):
        """Convert non-serializable objects to JSON-serializable types"""
        # Numpy types
        if isinstance(obj, (np.integer, np.signedinteger, np.unsignedinteger)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        
        # Torch types
        elif isinstance(obj, torch.Tensor):
            return obj.detach().cpu().numpy().tolist()
        elif isinstance(obj, torch.device):
            return str(obj)
        
        # Python decimal
        elif isinstance(obj, Decimal):
            return float(obj)
        
        # DateTime
        elif isinstance(obj, datetime):
            return obj.isoformat()
        
        # Fallback to default encoder
        return super().default(obj)


def convert_to_serializable(obj):
    """Recursively convert numpy/torch types to native Python types"""
    if obj is None:
        return None
    elif isinstance(obj, dict):
        return {key: convert_to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_serializable(item) for item in obj]
    elif isinstance(obj, (np.integer, np.signedinteger, np.unsignedinteger)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float16, np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, torch.Tensor):
        return obj.detach().cpu().numpy().tolist()
    else:
        return obj
