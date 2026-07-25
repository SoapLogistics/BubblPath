import logging
import numpy as np
from typing import Dict, Any

logger = logging.getLogger("HardwareSparsity")

class SparsityEngine:
    """
    N:M Sparsity engine designed for neural weight matrices.
    Implements a 2:4 sparsity pattern (zeroing out the smallest 2 absolute values
    in every 1D block of 4 elements) to cut memory overhead by 50% without massive accuracy loss,
    mirroring Nvidia Ampere sparse tensor cores.
    """

    @staticmethod
    def apply_2_4_sparsity(weight_matrix: np.ndarray) -> np.ndarray:
        """
        Applies a strict 2:4 sparsity mask to a given 2D numpy array.
        Assumes the last dimension is a multiple of 4.
        """
        # Ensure the matrix shape is compatible with blocks of 4
        if weight_matrix.shape[-1] % 4 != 0:
            logger.warning("Matrix dimension not a multiple of 4. Padding not currently implemented. Skipping sparsity.")
            return weight_matrix

        # Reshape to isolate blocks of 4
        original_shape = weight_matrix.shape
        reshaped = weight_matrix.reshape(-1, 4)

        # Find the indices of the 2 smallest absolute values in each block
        abs_weights = np.abs(reshaped)
        # np.argpartition is O(n) making this very fast
        smallest_indices = np.argpartition(abs_weights, 2, axis=1)[:, :2]

        # Create a mask and apply it
        mask = np.ones_like(reshaped, dtype=bool)
        # Using advanced indexing to set the smallest elements to False
        row_indices = np.arange(reshaped.shape[0])[:, None]
        mask[row_indices, smallest_indices] = False

        sparse_matrix = reshaped * mask
        return sparse_matrix.reshape(original_shape)

    @staticmethod
    def optimize_payload(weights: list) -> Dict[str, Any]:
        """API wrapper for the sparsity engine."""
        matrix = np.array(weights)
        original_size = matrix.nbytes

        sparse_matrix = SparsityEngine.apply_2_4_sparsity(matrix)

        # Calculate actual non-zero elements
        non_zero = np.count_nonzero(sparse_matrix)
        total_elements = sparse_matrix.size
        sparsity_ratio = 1.0 - (non_zero / total_elements)

        return {
            "original_shape": matrix.shape,
            "sparsity_achieved": round(sparsity_ratio * 100, 2),
            "optimized_weights": sparse_matrix.tolist()
        }
