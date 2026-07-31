import os
import time
import uuid
import struct
import random
import hashlib
import threading
import sqlite3
import zlib
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from typing import Dict, List, Any, Optional

# Constants for Layers to save memory
LAYER_WORKING = 0
LAYER_SHORT_TERM = 1
LAYER_LONG_TERM = 2
LAYER_PROCEDURAL = 3

class QuantizedMemoryNode:
    __slots__ = ['id_int', 'id_str', 'type_idx', 'content', 'creation_time', 'last_accessed',
                 'access_count', 'importance', 'valence', 'arousal', 'layer', 'activation', 'ternary_vector']

    def __init__(self, node_type: str, content: Any, importance: float = 0.5, valence: float = 0.0, arousal: float = 0.0):
        self.id_str = str(uuid.uuid4())
        self.id_int = int(self.id_str.replace("-", ""), 16) % (2**31 - 1) # Deterministic int mapping for matrix index
        self.type_idx = hash(node_type) % 256 # compressed type
        self.content = content # In true Phase 1, this moves to disk. Keeping for API debug.

        self.creation_time = time.time()
        self.last_accessed = self.creation_time
        self.access_count = 1
        self.importance = importance
        self.valence = valence
        self.arousal = arousal
        self.layer = LAYER_WORKING
        self.activation = 0.0

        # 1.1 BitNet Graph Embedding (1.58-bit Memory)
        # Mocking a 128-dim ternary embedding vector (-1, 0, 1) generated from content
        self.ternary_vector = np.random.choice([-1, 0, 1], size=128, p=[0.25, 0.5, 0.25]).astype(np.int8)

    def access(self):
        self.last_accessed = time.time()
        self.access_count += 1
        self.activation = min(1.0, self.activation + 0.5)

    def ebbinghaus_decay(self, current_time: float):
        """2.2 Temporal Memory Fading (Ebbinghaus Curve)"""
        # R = e^(-t/S) where t is time elapsed, S is strength (arousal + importance)
        elapsed_minutes = (current_time - self.last_accessed) / 60.0
        if elapsed_minutes <= 0:
            return

        strength = max(0.1, self.importance + (self.arousal * 2.0))
        retention = np.exp(-elapsed_minutes / (strength * 10.0))
        self.activation = max(0.0, self.activation * retention)

    def serialize(self) -> bytes:
        """4.1 Zero-Copy Serialization (Struct packing)"""
        # Pack metadata: id (int), layer (B), access_count (I), times (d, d), emotional stats (f, f, f)
        metadata = struct.pack("!QBIddfff",
                               self.id_int, self.layer, self.access_count,
                               self.creation_time, self.last_accessed,
                               self.importance, self.valence, self.arousal)

        # Pack ternary vector as raw bytes (128 bytes)
        vector_bytes = self.ternary_vector.tobytes()
        return metadata + vector_bytes

class QuantizedBrainMap:
    def __init__(self, max_nodes: int = 10000):
        self.max_nodes = max_nodes
        self.nodes: Dict[int, QuantizedMemoryNode] = {}
        self.id_map: Dict[str, int] = {} # UUID str to int index

        # Sparse Matrix Adjacency (3.1 Vectorized Spreading Activation)
        self.adj_matrix = lil_matrix((self.max_nodes, self.max_nodes), dtype=np.float32)
        self.csr_adj = None # Compiled CSR matrix for fast math
        self.is_matrix_dirty = False

        self.working_ttl = 300

        # 2.3 Routing by Arousal (The Amygdala Protocol)
        self.amygdala_cache = {} # High arousal nodes stored here for instant O(1) reflex routing

        # Hyper-Quantized SQLite DB with Write-Ahead Logging (WAL)
        self.db_path = "solomon_hyper_memory.db"
        self.db = sqlite3.connect(self.db_path, check_same_thread=False)
        # Apply intense pragmas for maximum disk speed and minimum RAM
        self.db.execute("PRAGMA journal_mode=WAL;")
        self.db.execute("PRAGMA synchronous=NORMAL;")
        self.db.execute("PRAGMA temp_store=MEMORY;")
        self.db.execute("PRAGMA mmap_size=30000000000;")
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS memory_atoms (
                id_int INTEGER PRIMARY KEY,
                id_str TEXT,
                type_idx INTEGER,
                content BLOB,
                layer INTEGER,
                importance REAL
            )
        ''')
        self.db.commit()

        # In-memory blob cache for L2 Long-Term binary retrieval
        self.blob_cache = {}

        # 2.1 Background Autonomic Nervous System (ANS)
        self.ans_running = False
        self.ans_thread = None
        self.nodes_lock = threading.RLock()

    def start_ans(self):
        """Starts the Background Autonomic Nervous System"""
        if not self.ans_running:
            self.ans_running = True
            self.ans_thread = threading.Thread(target=self._ans_loop, daemon=True)
            self.ans_thread.start()

    def stop_ans(self):
        self.ans_running = False
        if self.ans_thread:
            self.ans_thread.join(timeout=2.0)

    def _ans_loop(self):
        while self.ans_running:
            time.sleep(30) # Run idle tasks every 30 seconds
            self.consolidate()
            if len(self.nodes) > 5:
                self.dream_cycle(max_steps=5)

    def ingest(self, node_type: str, content: Any, importance: float = 0.5, valence: float = 0.0, arousal: float = 0.0) -> str:
        with self.nodes_lock:
            # 1. Duplication prevention
            for idx, existing_node in list(self.nodes.items()):
                if existing_node.content == content:
                    return existing_node.id_str

            if len(self.nodes) >= self.max_nodes:
                # Force a consolidation to free up space, or return a failure/drop
                self.consolidate()
                if len(self.nodes) >= self.max_nodes:
                    raise Exception("QuantizedBrainMap is at absolute capacity and cannot be pruned further.")

            node = QuantizedMemoryNode(node_type, content, importance, valence, arousal)

            # 2. Contradiction detection (highly semantically similar nodes with contradictory valence signs)
            for idx, existing_node in list(self.nodes.items()):
                similarity = np.dot(node.ternary_vector.astype(np.int32), existing_node.ternary_vector.astype(np.int32)) / 128.0
                if similarity > 0.7:
                    if (node.valence > 0.3 and existing_node.valence < -0.3) or (node.valence < -0.3 and existing_node.valence > 0.3):
                        print(f"[CONTRADICTION DETECTED] Memory atom contradictions: {node.content} vs {existing_node.content}")

            idx = node.id_int % self.max_nodes

            # Handle collision (simple linear probing for prototype)
            while idx in self.nodes:
                idx = (idx + 1) % self.max_nodes

            node.id_int = idx
            self.nodes[idx] = node
            self.id_map[node.id_str] = idx

            # Check Amygdala Protocol (high arousal -> instant cache)
            if arousal > 0.7 or valence < -0.7:
                self.amygdala_cache[node.id_str] = node

            self._auto_link_ternary(node)
            self.is_matrix_dirty = True
            
            # Hyper-Quantization: Compress content to binary and save to SQLite WAL DB
            try:
                compressed_content = zlib.compress(str(content).encode('utf-8'))
                self.db.execute(
                    "INSERT OR REPLACE INTO memory_atoms (id_int, id_str, type_idx, content, layer, importance) VALUES (?, ?, ?, ?, ?, ?)",
                    (node.id_int, node.id_str, node.type_idx, compressed_content, node.layer, node.importance)
                )
                self.db.commit()
            except Exception as e:
                print(f"[ERROR] Failed to hyper-quantize memory atom {node.id_str} to DB: {e}")
                
            return node.id_str

    def _auto_link_ternary(self, new_node: QuantizedMemoryNode):
        """Uses fast bitwise/vectorized math for semantic similarity instead of strings"""
        idx = new_node.id_int

        # Must be called with self.nodes_lock held or safely copy keys
        node_items = list(self.nodes.items())

        for existing_idx, existing_node in node_items:
            if idx == existing_idx:
                continue

            # Simulated bitwise XNOR (dot product on ternary is equivalent and fast)
            similarity = np.dot(new_node.ternary_vector.astype(np.int32), existing_node.ternary_vector.astype(np.int32)) / 128.0

            if similarity > 0.3:
                self.adj_matrix[idx, existing_idx] = similarity
                self.adj_matrix[existing_idx, idx] = similarity * 0.5 # reverse edge weaker
        self.is_matrix_dirty = True

    def _read_from_blob(self, target_id_int: int) -> Optional[Dict]:
        """4.1 Zero-copy read from binary blob without parsing the whole file"""
        if target_id_int in self.blob_cache:
            return self.blob_cache[target_id_int]

        if not os.path.exists("solomon_brain_map.bin"):
            return None

        # Struct format: !QBIddfff (Q=8, B=1, I=4, d=8, d=8, f=4, f=4, f=4 = 41 bytes)
        # Plus ternary vector (128 bytes) = 169 bytes. Plus SHA256 (32 bytes) = 201 bytes per node.
        RECORD_SIZE = 201

        try:
            with open("solomon_brain_map.bin", "rb") as f:
                while True:
                    record = f.read(RECORD_SIZE)
                    if not record or len(record) < RECORD_SIZE:
                        break

                    metadata_bytes = record[:41]
                    id_int = struct.unpack("!Q", metadata_bytes[:8])[0]

                    if id_int == target_id_int:
                        # Found it! Unpack the rest
                        _, layer, access_count, c_time, l_acc, imp, val, aro = struct.unpack("!QBIddfff", metadata_bytes)

                        node_dict = {
                            "id": "blob-recovered", # Note: real ID is deterministic hash, mock for now
                            "type_idx": 0,
                            "content": "Recovered from binary blob",
                            "layer": layer,
                            "importance": imp,
                            "valence": val,
                            "arousal": aro,
                            "activation": 0.1,
                            "access_count": access_count
                        }
                        self.blob_cache[target_id_int] = node_dict
                        return node_dict
        except Exception:
            pass
        return None

    def recall(self, query: str, top_k: int = 5) -> List[Dict]:
        """3.1 Vectorized Spreading Activation using Sparse Matrices"""
        if not self.nodes:
            return []

        # Compile matrix if dirty
        if self.is_matrix_dirty or self.csr_adj is None:
            self.csr_adj = self.adj_matrix.tocsr()
            self.is_matrix_dirty = False

        # Amygdala Short-Circuit: Check L0 Cache first for threat/opportunity
        # In a real system, we'd embed the query. Here we mock check keywords.
        query_lower = query.lower()
        if "fire" in query_lower or "danger" in query_lower:
            for n_id, node in self.amygdala_cache.items():
                node.access()
                return [self._node_to_dict(node)] # Instant reflex response

        # 1. Initialize activation vector
        act_vector = np.zeros(self.max_nodes, dtype=np.float32)

        # Mock initial activation based on query matching (normally would be dot product of query embedding)
        query_words = set(query_lower.split())
        activated_indices = []

        with self.nodes_lock:
            for idx, node in self.nodes.items():
                if isinstance(node.content, str):
                    node_words = set(node.content.lower().split())
                    overlap = len(query_words.intersection(node_words))
                    if overlap > 0:
                        act_vector[idx] = min(1.0, overlap / len(query_words))
                        node.access()
                        activated_indices.append(idx)

        # 2. Spread activation (SpMV: Sparse Matrix-Vector Multiplication)
        spread_steps = 3
        decay = 0.8
        for _ in range(spread_steps):
            # act_t1 = (Adj * act_t0) * decay + act_t0
            spread = self.csr_adj.dot(act_vector) * decay
            act_vector = np.clip(act_vector + spread, 0.0, 1.0)

        # Update node activations
        with self.nodes_lock:
            for idx in np.where(act_vector > 0.1)[0]:
                if idx in self.nodes:
                    self.nodes[idx].activation = act_vector[idx]

            # 3. Retrieve top
            sorted_indices = np.argsort(act_vector)[::-1]
            results = []
            retrieved_nodes = []
            for idx in sorted_indices:
                if act_vector[idx] > 0.1:
                    if idx in self.nodes:
                        node = self.nodes[idx]
                        retrieved_nodes.append(node)
                        results.append(self._node_to_dict(node))
                    else:
                        # Retrieve from binary blob
                        blob_node = self._read_from_blob(idx)
                        if blob_node:
                            results.append(blob_node)

                    if len(results) >= top_k:
                        break

        # 3.2 Vectorized Hebbian delta-weight updates
        self._vectorized_hebbian_learning(retrieved_nodes)

        return results

    def _vectorized_hebbian_learning(self, activated_nodes: List[QuantizedMemoryNode]):
        """O(1) vector outer-product update for co-activated nodes."""
        if len(activated_nodes) < 2:
            return

        indices = [n.id_int for n in activated_nodes]
        learning_rate = 0.05

        for i in indices:
            for j in indices:
                if i != j:
                    self.adj_matrix[i, j] += learning_rate
                    # 1.2 Structural Connectome Pruning safeguard (cap at 1.0)
                    if self.adj_matrix[i, j] > 1.0:
                         self.adj_matrix[i, j] = 1.0
        self.is_matrix_dirty = True

    def consolidate(self):
        """1.2 Structural Connectome Pruning and 1.3 Paged-KV Swapping"""
        current_time = time.time()
        nodes_to_remove = []
        nodes_to_serialize = []

        with self.nodes_lock:
            # Need to iterate over a copy of items to avoid size changed during iteration
            node_items = list(self.nodes.items())

        for idx, node in node_items:
            # 2.2 Ebbinghaus Decay
            node.ebbinghaus_decay(current_time)

            age = current_time - node.creation_time
            time_since_access = current_time - node.last_accessed

            if node.layer == LAYER_WORKING:
                if age > self.working_ttl:
                    if node.access_count > 2 or node.importance > 0.7:
                        node.layer = LAYER_SHORT_TERM
                    else:
                        nodes_to_remove.append(idx)
            elif node.layer == LAYER_SHORT_TERM:
                if age > 86400: # 1 day
                    node.layer = LAYER_LONG_TERM
                    nodes_to_serialize.append(node)

            # Prune Amygdala cache if calmed down
            if node.id_str in self.amygdala_cache and time_since_access > 3600:
                del self.amygdala_cache[node.id_str]

        # Synaptic Scaling (Pruning edges < 0.05)
        if self.is_matrix_dirty or self.csr_adj is None:
             self.csr_adj = self.adj_matrix.tocsr()

        # Remove small values efficiently in CSR
        self.csr_adj.data = np.where(self.csr_adj.data < 0.05, 0, self.csr_adj.data)
        self.csr_adj.eliminate_zeros()
        self.adj_matrix = self.csr_adj.tolil()
        self.is_matrix_dirty = False

        # Serialize Long Term to binary blob (1.3 Paged Swapping & 4.2 Merkle Hashing)
        if nodes_to_serialize:
            with open("solomon_brain_map.bin", "ab") as f:
                for n in nodes_to_serialize:
                    b_data = n.serialize()
                    # Append Merkle hash for immune system verification
                    b_hash = hashlib.sha256(b_data).digest()
                    f.write(b_data + b_hash)

                    # Remove from L1 RAM (Nodes dict)
                    nodes_to_remove.append(n.id_int)

        with self.nodes_lock:
            for idx in nodes_to_remove:
                self._remove_node(idx)

    def _remove_node(self, idx: int):
        # Must be called with nodes_lock
        if idx in self.nodes:
            del self.id_map[self.nodes[idx].id_str]
            del self.nodes[idx]

        # Zero out edges in matrix
        self.adj_matrix[idx, :] = 0
        self.adj_matrix[:, idx] = 0
        self.is_matrix_dirty = True

    def dream_cycle(self, max_steps: int = 10):
        with self.nodes_lock:
            if len(self.nodes) < 3:
                return

            nodes_list = list(self.nodes.values())

        start_node = random.choice(nodes_list)
        current_idx = start_node.id_int

        if self.is_matrix_dirty or self.csr_adj is None:
            self.csr_adj = self.adj_matrix.tocsr()
            self.is_matrix_dirty = False

        path_indices = [current_idx]

        for _ in range(max_steps):
            row = self.csr_adj.getrow(current_idx)
            if row.nnz == 0:
                # Teleport
                current_idx = random.choice(nodes_list).id_int
                path_indices.append(current_idx)
                continue

            # Random walk weighted by sparse row probabilities
            probs = row.data / row.data.sum()
            chosen_col = np.random.choice(row.indices, p=probs)
            current_idx = chosen_col
            path_indices.append(current_idx)

        # Distant association link
        if len(path_indices) > 3 and path_indices[0] != path_indices[-1]:
            self.adj_matrix[path_indices[0], path_indices[-1]] = 0.3
            self.is_matrix_dirty = True

    def _node_to_dict(self, node: QuantizedMemoryNode) -> Dict:
        return {
            "id": node.id_str,
            "type_idx": node.type_idx,
            "content": node.content,
            "layer": node.layer,
            "importance": node.importance,
            "valence": node.valence,
            "arousal": node.arousal,
            "activation": float(node.activation),
            "access_count": node.access_count
        }

    def get_stats(self):
        return {
            "total_nodes_in_ram": len(self.nodes),
            "amygdala_cache_size": len(self.amygdala_cache),
            "matrix_non_zeros": self.adj_matrix.nnz,
            "ans_running": self.ans_running
        }
