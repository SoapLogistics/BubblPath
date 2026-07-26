import { renderExpansion } from './src/reader-expansion.js';

// The remaining core application logic
console.log("App initializing...");
const exp = renderExpansion("some data");
console.log(exp);
