import assert from 'assert';
import { renderExpansion } from './src/reader-expansion.js';

// Simple test for contract
assert.strictEqual(renderExpansion("test data"), "<div>Expansion: test data</div>");
console.log('Contract demo passed.');
