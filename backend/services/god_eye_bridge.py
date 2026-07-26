import numpy as np
from flask import Blueprint, jsonify
import struct
import os
import hashlib
from typing import List, Dict

god_eye_blueprint = Blueprint('god_eye', __name__)

@god_eye_blueprint.route('/api/memory/graph.json', methods=['GET'])
def get_memory_graph():
    """
    Serializes the memory blob into a frontend-friendly format.
    Reads solomon_brain_map.bin and returns all nodes and an optimized spatial layout.
    """
    nodes = []
    edges = []

    if not os.path.exists("solomon_brain_map.bin"):
        return jsonify({"nodes": nodes, "edges": edges})

    RECORD_SIZE = 201

    try:
        with open("solomon_brain_map.bin", "rb") as f:
            while True:
                record = f.read(RECORD_SIZE)
                if not record or len(record) < RECORD_SIZE:
                    break

                metadata_bytes = record[:41]
                id_int, layer, access_count, creation_time, last_accessed, importance, valence, arousal = struct.unpack("!QBIddfff", metadata_bytes)

                vector_bytes = record[41:169] # 128 bytes

                # Semantic Positioning: Use the first 3 chunks of the ternary vector to map to 3D space
                # This groups semantically similar memories natively without arbitrary hashing

                vec = np.frombuffer(vector_bytes, dtype=np.int8)

                # Simple projection: sum sections of the vector for x, y, z
                chunk_size = len(vec) // 3
                x = (float(np.sum(vec[:chunk_size])) / chunk_size) * 800
                y = (float(np.sum(vec[chunk_size:chunk_size*2])) / chunk_size) * 800
                z = (float(np.sum(vec[chunk_size*2:chunk_size*3])) / chunk_size) * 800

                nodes.append({
                    "id": str(id_int),
                    "idx": id_int, # pass integer idx for edge mapping
                    "x": x,
                    "y": y,
                    "z": z,
                    "layer": layer,
                    "valence": valence,
                    "arousal": arousal,
                    "importance": importance
                })

        # Add edges from live memory matrix if app is running
        from app import unified_memory
        if hasattr(unified_memory, 'csr_adj') and unified_memory.csr_adj is not None:
            coo = unified_memory.csr_adj.tocoo()

            # Map sparse index pairs to real int IDs for the frontend
            # Create a reverse map for nodes present in blob


            for row, col, val in zip(coo.row, coo.col, coo.data):
                if val > 0.1: # Only strong edges
                    edges.append({
                        "source": int(row),
                        "target": int(col),
                        "weight": float(val)
                    })

    except Exception as e:
        print(f"Error reading brain map: {e}")
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "nodes": nodes,
        "edges": edges
    })

# Engine Registry Metadata
route_key = "god_eye_bridge"
readiness_key = "active"
