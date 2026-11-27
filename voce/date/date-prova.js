// Prova delle grafie dei numeri: 6 frasi piene di date, ciascuna in 4 grafie del testo letto.
const fs = require("fs"); const p = require("./prepara.js");
const F = ["Il 29 maggio 1176 la Lega Lombarda sconfisse a Legnano l'imperatore Federico I Barbarossa.",
  "Nel 1256 i Lucchesi e i Fiorentini vinsero a Ponte a Serchio; nel 1289 Firenze vinse anche a Campaldino.",
  "Enrico VII (1310-1313) scese in Italia per farsi incoronare imperatore a Roma.",
  "Nel XIII secolo Federico II fece costruire castelli in tutto il Regno di Sicilia.",
  "La battaglia della Falconaria si combatté il 1° dicembre 1299, quando il papa era Bonifacio VIII.",
  "Nel 1277 Pisa aveva forse 40.000 o 50.000 abitanti; tra XII e XIII secolo era una grande potenza del mare."];
const V = [["A-attaccato", { numeri: "attaccato" }], ["B-separato", { numeri: "separato" }], ["C-misto", { numeri: "misto" }], ["D-cifre", { cifre: true }]];
const out = []; F.forEach((t, i) => V.forEach(([n, o]) => out.push({ chiave: "d" + (i + 1) + "-" + n, gruppo: "date", dove: "prova-date", testo: t, lettura: p.leggibile(t, o) })));
out.forEach(x => x.frasi = p.frasi(x.lettura));
fs.writeFileSync(process.argv[2], JSON.stringify(out, null, 1)); out.filter(x => /d3/.test(x.chiave)).forEach(x => console.log(x.chiave, "|", x.lettura));
