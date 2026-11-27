/* Preparazione dei testi del narratore per la sintesi con XTTS v2 (voce Viktor Eka).
   Il contenuto non cambia: numeri, date e numeri romani passano in lettere, i nomi stranieri prendono una grafia
   che il modello italiano legge bene, le virgolette e le parentesi diventano pause, e ogni testo si divide in frasi
   senza punto finale (XTTS a volte legge il punto come parola). La chiave resta quella del testo originale.
   Uso: node prepara.js testi-tutti.json uscita.json */
'use strict';
const fs = require('fs');

const U = ['zero', 'uno', 'due', 'tre', 'quattro', 'cinque', 'sei', 'sette', 'otto', 'nove', 'dieci', 'undici', 'dodici', 'tredici',
  'quattordici', 'quindici', 'sedici', 'diciassette', 'diciotto', 'diciannove'];
const D = ['', '', 'venti', 'trenta', 'quaranta', 'cinquanta', 'sessanta', 'settanta', 'ottanta', 'novanta'];
function sotto100(n) {
  if (n < 20) return U[n];
  const d = D[Math.floor(n / 10)], u = n % 10;
  if (!u) return d;
  const pref = (u === 1 || u === 8) ? d.slice(0, -1) : d;
  return pref + (u === 3 ? 'tré' : U[u]);
}
function sotto1000(n) {
  if (n < 100) return sotto100(n);
  const c = Math.floor(n / 100), r = n % 100;
  let s = c === 1 ? 'cento' : U[c] + 'cento';
  if (!r) return s;
  if (Math.floor(r / 10) === 8 || r === 8) s = s.slice(0, -1);   // centottanta, milleduecentottantanove
  return s + sotto100(r);
}
/* Grafia dei numeri da mille in su (STILE.numeri), scelta per ciascuna voce con le prove sulle date:
   attaccato  milleduecentocinquantasei
   separato   mille duecento cinquantasei
   misto      milleduecento cinquantasei */
const STILE = { numeri: 'attaccato', cifre: false };
function cardinale(n) {
  n = Math.floor(n);
  if (n < 1000) return sotto1000(n);
  if (n < 1000000) {
    const m = Math.floor(n / 1000), r = n % 1000;
    const s = m === 1 ? 'mille' : sotto1000(m) + 'mila';
    if (!r) return s;
    if (STILE.numeri === 'attaccato') return s + sotto1000(r);
    const c = Math.floor(r / 100), d = r % 100;
    const cento = c ? (c === 1 ? 'cento' : U[c] + 'cento') : '';
    const resto = d ? finale(sotto100(d)) : '';
    if (STILE.numeri === 'separato') return [s, cento, resto].filter(Boolean).join(' ');
    return [s + cento, resto].filter(Boolean).join(' ');
  }
  const mi = Math.floor(n / 1000000), r = n % 1000000;
  const s = mi === 1 ? 'un milione' : cardinale(mi) + ' milioni';
  return r ? s + ' ' + cardinale(r) : s;
}
// forma finale: «tré» si scrive «tre» solo se il numero è proprio 3
function finale(s) { return s === 'tré' ? 'tre' : s; }
const ORD = ['', 'primo', 'secondo', 'terzo', 'quarto', 'quinto', 'sesto', 'settimo', 'ottavo', 'nono', 'decimo'];
function ordinale(n) {
  if (n <= 10) return ORD[n];
  let c = cardinale(n);
  if (c.endsWith('tré')) return c.slice(0, -1) + 'eesimo';
  if (c.endsWith('sei')) return c + 'esimo';
  return c.slice(0, -1) + 'esimo';
}
function romano(s) {
  const v = { I: 1, V: 5, X: 10, L: 50, C: 100, D: 500, M: 1000 }; let t = 0;
  for (let i = 0; i < s.length; i++) { const a = v[s[i]], b = v[s[i + 1]] || 0; t += a < b ? -a : a; }
  return t;
}
function numeroTesto(str) {   // "8.000" "1194" "97,20" "3,5"
  const [int, dec] = str.split(',');
  const n = parseInt(int.replace(/\./g, ''), 10);
  let s = finale(cardinale(n));
  if (dec) s += ' virgola ' + (dec.length === 2 && dec[0] !== '0' ? finale(cardinale(parseInt(dec, 10))) : dec.split('').map(c => U[+c]).join(' '));
  return s;
}

// grafia di lettura per i nomi stranieri (il testo mostrato non cambia)
const NOMI = [
  ['Hohenstaufen', 'Oenstàufen'], ['Valois', 'Valuà'], ['Arras', 'Arràs'], ['Durfort', 'Durfòr'], ['Valéry', 'Valerì'], ['Valery', 'Valerì'],
  ['Bruges', 'Brùges'], ['Britaud', 'Britò'], ['Cousances', 'Cusàns'], ['Drouet', 'Druè'], ['Welf', 'Velf'], ['Waiblingen', 'Vàiblinghen'],
  ['Mirepoix', 'Mirpuà'], ['Gilles', 'Gil'], ['Annweiler', 'Ànvailer'], ['Guy', 'Ghì'], ['Foucois', 'Fucuà'], ['Nogaret', 'Nogarè'],
  ['Aimeric', 'Aimerìc'], ['Weinsberg', 'Vàinsberg'], ['Érard', 'Eràr'], ['Crécy', 'Cressì'], ['Canterbury', 'Cànterberi'],
  ['Villard', 'Villàr'], ['Honnecourt', 'Oncùr'], ['Jean', 'Gian'], ['Jubayr', 'Giubàir'], ['Hawqal', 'Àucal'], ['Baghdad', 'Bagdàd'],
  ['Jacopino', 'Iacopino'], ['Jacopo', 'Iacopo'], ['Jesi', 'Iesi'], ['briefing', 'brìfing'], ['UNESCO', 'Unesco'],
  ['FLORENTIA', 'Florentia'], ['LIBERTAS', 'Libertas'], ['Baden', 'Bàden']
];
// opere con canti: «Inferno X» → «Inferno, canto decimo»
const OPERE = 'Inferno|Purgatorio|Paradiso';
/* Accenti tonici nel testo letto, ricontrollati una per una il 27/11/2026 (fonti in ACCENTI.txt): si accentano solo
   parole sdrucciole verificate su Treccani o sulla trascrizione AFI di Wikipedia, oppure parole che Kokoro legge male.
   Nel dubbio la parola resta senza accento. Tolte dopo la correzione di Giovanni: Màrsala (è Marsàla), Lùcera (Lucèra),
   Montàperti (Montapèrti), Dòvadola (Dovàdola); Kokoro le legge già bene senza accento. Rotari si legge Rotàri:
   Kokoro senza accento legge «Ròtari», quindi qui riceve l'accento corretto.
   Forma: [parola o espressione, forma accentata]; le espressioni servono per gli omografi (principi). */
const ACCENTI = [
  ['principi angioini', 'prìncipi angioini'], ['principi opposti', 'princìpi opposti'],
  ['segale', 'ségale'], ['mangano', 'màngano'], ['fondaco', 'fóndaco'], ['estimo', 'èstimo'], ['companatico', 'companàtico'],
  ['sughera', 'sùghera'], ['mantici', 'màntici'], ['incudini', 'incùdini'], ['argani', 'àrgani'], ['decima', 'dècima'],
  ['Procida', 'Pròcida'], ['Fiesole', 'Fièsole'], ['Cassaro', 'Càssaro'], ['Caccamo', 'Càccamo'], ['Eboli', 'Èboli'],
  ['Brindisi', 'Brìndisi'], ['Marettimo', 'Marèttimo'], ['Tiepido', 'Tièpido'], ['Rotari', 'Rotàri']
];

// opz: { numeri: 'attaccato' | 'separato' | 'misto', cifre: true per lasciare cifre e numeri romani al modello }
function leggibile(t, opz) {
  Object.assign(STILE, { numeri: 'attaccato', cifre: false, accenti: false }, opz || {});
  let s = ' ' + t + ' ';
  NOMI.forEach(([a, b]) => { s = s.replace(new RegExp('(?<![\\wÀ-ÿ])' + a + '(?![\\wÀ-ÿ])', 'g'), b); });
  if (STILE.accenti) ACCENTI.forEach(([a, b]) => { s = s.replace(new RegExp('(?<![\\wÀ-ÿ])' + a + '(?![\\wÀ-ÿ])', 'g'), b); });
  // virgolette tolte (la frase citata resta), barre dei versi come pause
  s = s.replace(/[«»"“”]/g, '').replace(/\s\/\s/g, ', ');
  // articolo dantesco «'l» letto come «el» (Kokoro altrimenti legge la lettera «elle»); «'nnanellata» come «innanellata»
  s = s.replace(/(\s)['’]l(?=\s)/g, '$1el').replace(/(\s)['’]nn/g, '$1inn');
  if (STILE.cifre) return s.replace(/\s*\(\s*/g, ', ').replace(/\s*\)\s*([.,;:!?])/g, '$1').replace(/\s*\)\s*/g, ', ').replace(/\s+/g, ' ').trim();
  // riferimenti danteschi
  s = s.replace(new RegExp('\\b(' + OPERE + ') ([IVXL]+), (\\d+)-(\\d+)', 'g'), (m, o, r, a, b) => o + ', canto ' + ordinale(romano(r)) + ', versi ' + numeroTesto(a) + ' e ' + numeroTesto(b));
  s = s.replace(new RegExp('\\b(' + OPERE + ') ([IVXL]+)\\b', 'g'), (m, o, r) => o + ', canto ' + ordinale(romano(r)));
  s = s.replace(/\bcanto ([IVXL]+)\b/g, (m, r) => 'canto ' + ordinale(romano(r)));
  s = s.replace(/\b([IVX]+)-([IVX]+)\b/g, '$1 e $2');
  // secoli: «XIII secolo», «secolo XIII», «tra XI e XIII secolo»
  s = s.replace(/\b([IVX]+)((?: e (?:nel |il )?[IVX]+)*) secol/g, (m, r, resto) => ordinale(romano(r)) + resto.replace(/[IVX]+/g, x => ordinale(romano(x))) + ' secol');
  s = s.replace(/\b(secol[oi]) ([IVX]+)\b/g, (m, w, r) => w + ' ' + ordinale(romano(r)));
  // numeri dei sovrani e dei papi: un romano dopo un nome proprio (non a inizio frase, non seguito da apostrofo)
  s = s.replace(/([A-ZÀ-Ý][a-zà-ÿ]+) ((?:[IVX]{1,5}))(?![\wÀ-ÿ'’])/g, (m, nome, r) => {
    if (r === 'I' && /^(E|O|A|Ma|Se|Poi|Così)$/.test(nome)) return m;
    const n = romano(r); if (!n || n > 30) return m;
    return nome + ' ' + ordinale(n);
  });
  // altri romani di almeno due lettere (libro XII, dell'XI): ordinali
  s = s.replace(/(^|[\s'’])([IVX]{2,})(?![\wÀ-ÿ])/g, (m, a, r) => a + ordinale(romano(r)));
  // date e numeri
  s = s.replace(/(\d+)°/g, (m, n) => ordinale(+n));
  s = s.replace(/\((\d{3,4})-(\d{3,4})\)/g, (m, a, b) => ', dal ' + a + ' al ' + b + ',');
  s = s.replace(/(\d[\d.]*)-(\d[\d.]*)/g, (m, a, b) => /\./.test(a) ? a + ' o ' + b : a + ' e ' + b);
  s = s.replace(/\d+(?:\.\d{3})*(?:,\d+)?/g, m => numeroTesto(m));
  s = s.replace(/%/g, ' per cento');
  // parentesi come pause
  s = s.replace(/\s*\(\s*/g, ', ').replace(/\s*\)\s*([.,;:!?])/g, '$1').replace(/\s*\)\s*/g, ', ');
  s = s.replace(/\s+,/g, ',').replace(/,\s*,/g, ',').replace(/,\s*([.;:!?])/g, '$1').replace(/([;:!?])\s*,/g, '$1').replace(/([?!])\./g, '$1').replace(/^\s*,\s*/, '').replace(/\s+/g, ' ').trim();
  return s;
}

const MAXF = 180;   // XTTS in italiano regge circa 213 caratteri per frase
function frasi(s) {
  const parti = s.split(/(?<=[.!?;:…])\s+/).map(x => x.trim()).filter(Boolean);
  const out = [];
  parti.forEach(p => {
    if (p.length <= MAXF) { out.push(p); return; }
    // frase lunga: taglio alle virgole più vicine al limite
    let resto = p;
    while (resto.length > MAXF) {
      let i = resto.lastIndexOf(', ', MAXF); if (i < 40) i = resto.indexOf(', ', MAXF);
      if (i < 0) break;
      out.push(resto.slice(0, i + 1)); resto = resto.slice(i + 2);
    }
    out.push(resto);
  });
  // punteggiatura finale tolta (resta il punto interrogativo, che dà l'intonazione); frasi brevissime unite alla seguente
  const pul = out.map(f => f.replace(/[.;:,…]+$/, '').replace(/!+$/, '').trim()).filter(f => /[A-Za-zÀ-ÿ0-9]/.test(f));
  const fin = [];
  for (let i = 0; i < pul.length; i++) {
    let f = pul[i];
    while (f.length < 20 && i + 1 < pul.length && !/\?$/.test(f) && (f + ', ' + pul[i + 1]).length <= MAXF) { f = f + ', ' + pul[++i]; }
    fin.push(f);
  }
  return fin;
}

/* Preparazione per ciascuna voce, scelta con la prova delle date del 27/11/2026 (Whisper e durate):
   - le cifre lasciate al modello vanno escluse per entrambe: Chatterbox le storpia («duodo cente», «5333») e Kokoro legge
     «1°» come «1 gradi» e «40.000» come «40, l'ero 00»;
   - fra le tre grafie in lettere le trascrizioni risultano corrette per entrambe le voci; la grafia attaccata dà le letture
     più scorrevoli e più brevi (nessuna pausa fra «mille» e «duecento»), e per Chatterbox la grafia separata ha prodotto
     una ripetizione («a Roma, a Roma»). Le due voci hanno quindi profili distinti, oggi con la stessa grafia. */
const PROFILI = { nicola: { numeri: 'attaccato', accenti: true }, f07: { numeri: 'attaccato', accenti: true } };

if (require.main === module) {
  // Uso: node prepara.js testi-tutti.json uscita.json [--voce nicola|f07]
  const [inp, out] = process.argv.slice(2);
  const iv = process.argv.indexOf('--voce'), voce = iv > 0 ? process.argv[iv + 1] : 'nicola';
  if (!PROFILI[voce]) throw new Error('voce sconosciuta: ' + voce);
  const L = JSON.parse(fs.readFileSync(inp, 'utf8'));
  const R = L.map(x => { const lett = leggibile(x.testo, PROFILI[voce]); return { chiave: x.chiave, gruppo: x.gruppo, dove: x.dove, testo: x.testo, lettura: lett, frasi: frasi(lett) }; });
  fs.writeFileSync(out, JSON.stringify(R, null, 1));
  const resti = R.filter(x => /\d|\b[IVX]{2,}\b/.test(x.lettura));
  console.log('testi', R.length, 'frasi', R.reduce((a, x) => a + x.frasi.length, 0), 'caratteri letti', R.reduce((a, x) => a + x.lettura.length, 0));
  console.log('con cifre o romani rimasti:', resti.length); resti.slice(0, 20).forEach(x => console.log('  ', x.chiave, x.lettura.slice(0, 200)));
}
module.exports = { leggibile, frasi, cardinale, ordinale, PROFILI, ACCENTI };
