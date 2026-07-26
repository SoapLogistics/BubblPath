const artifactStore = new Map();

export function storeArtifact(id, fullData) {
    // Store full artifact once
    if (!artifactStore.has(id)) {
        artifactStore.set(id, fullData);
    }
}

export function recallSummary(id) {
    // Recall compact summary by default
    const fullData = artifactStore.get(id);
    if (!fullData) return null;

    return {
        id: id,
        summary: fullData.substring(0, 100) + '...',
        hasFull: true
    };
}

export function openFullArtifact(id) {
    // Load full artifact only on explicit open
    return artifactStore.get(id);
}
