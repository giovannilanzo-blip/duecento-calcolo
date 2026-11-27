// Estrae l'elenco completo dei testi del narratore riusando elenco() di g2/strumenti/voce-estrai.js, senza scrivere nulla in g2.
'use strict';
const fs = require('fs'), path = require('path');
const G = process.argv[2], OUT = process.argv[3];
let src = fs.readFileSync(path.join(G, 'strumenti', 'voce-estrai.js'), 'utf8');
src = src.slice(0, src.indexOf('const arg = process.argv'));
src = src.replace("const ROOT = path.join(__dirname, '..');", 'const ROOT = ' + JSON.stringify(G) + ';');
// con una voce sola anche i testi brevi delle missioni e del Codice regionale passano alla voce registrata
const tutti = process.argv.includes('--tutti');
if (tutti) src = src.replace('const MINIMO = 60;', 'const MINIMO = 0;');
const mod = { exports: {} };
new Function('require', 'module', '__dirname', src + '\nmodule.exports = { elenco, leggiIndice };')(require, mod, path.join(G, 'strumenti'));
const lista = mod.exports.elenco(), ind = mod.exports.leggiIndice();
const g = {};
lista.forEach(x => { const r = g[x.gruppo] = g[x.gruppo] || { testi: 0, caratteri: 0, gia_elevenlabs: 0 }; r.testi++; r.caratteri += x.caratteri; if (ind.registrati[x.chiave]) r.gia_elevenlabs++; });
const chiavi = new Set(lista.map(x => x.chiave));
const orfani = Object.keys(ind.registrati).filter(k => !chiavi.has(k));
fs.writeFileSync(OUT, JSON.stringify(lista.map(x => ({ chiave: x.chiave, gruppo: x.gruppo, dove: x.dove, testo: x.testo })), null, 1));
console.log(JSON.stringify(g, null, 1));
console.log('totale testi', lista.length, 'caratteri', lista.reduce((a, x) => a + x.caratteri, 0), 'orfani nell\'indice', orfani.length, orfani.slice(0, 5));
