// Prova degli accenti tonici: 15 frasi con parole a rischio, ciascuna senza e con l'accento grafico nel testo letto.
const fs = require('fs');
const F = [
  ['I poveri mangiavano pani di segale, orzo, miglio o panico.', [['segale', 'ségale'], ['panico', 'panìco']]],
  ['Le macchine si chiamavano mangano, petriera e briccola.', [['mangano', 'màngano'], ['briccola', 'brìccola']]],
  ['Il mercante teneva il fondaco, pagava l\'estimo e mangiava il companatico.', [['fondaco', 'fòndaco'], ['estimo', 'èstimo'], ['companatico', 'companàtico']]],
  ['Nei boschi c\'erano il leccio, la sughera e il castagno.', [['sughera', 'sùghera']]],
  ['I fabbri usavano mantici, martelli e incudini.', [['mantici', 'màntici'], ['incudini', 'incùdini']]],
  ['Giovanni da Procida passò da Lucera e da Fiesole.', [['Procida', 'Pròcida'], ['Lucera', 'Lùcera'], ['Fiesole', 'Fièsole']]],
  ['Le navi andavano da Trapani a Marsala, poi a Cagliari e a Tunisi.', [['Trapani', 'Tràpani'], ['Marsala', 'Màrsala'], ['Cagliari', 'Càgliari'], ['Tunisi', 'Tùnisi']]],
  ['Dopo Montaperti, a Empoli, Farinata ricordò il fiume Arbia.', [['Montaperti', 'Montàperti'], ['Empoli', 'Èmpoli'], ['Arbia', 'Àrbia']]],
  ['Il Cassaro di Palermo porta verso il castello di Caccamo.', [['Cassaro', 'Càssaro'], ['Caccamo', 'Càccamo']]],
  ['I conti Guidi di Dovadola conoscevano l\'Editto di Rotari.', [['Dovadola', 'Dòvadola'], ['Rotari', 'Ròtari']]],
  ['Iacopo de\' Pazzi, Pietro Tiepolo ed Enrico Dandolo.', [['Iacopo', 'Iàcopo'], ['Tiepolo', 'Tièpolo'], ['Dandolo', 'Dàndolo']]],
  ['Filippo di Taranto, il conte di Eboli e la città di Capua.', [['Taranto', 'Tàranto'], ['Eboli', 'Èboli'], ['Capua', 'Càpua']]],
  ['Partì da Brindisi e passò vicino a Marettimo e a Peretola.', [['Brindisi', 'Brìndisi'], ['Marettimo', 'Marèttimo'], ['Peretola', 'Perètola']]],
  ['I due principi angioini pagavano la decima.', [['principi', 'prìncipi'], ['decima', 'dècima']]],
  ['Pistoia, Legnano, Modena, Bergamo, Novara, Padova e Mantova.', [['Pistoia', 'Pistóia'], ['Legnano', 'Legnàno'], ['Modena', 'Mòdena'], ['Bergamo', 'Bèrgamo'], ['Novara', 'Nòvara'], ['Padova', 'Pàdova'], ['Mantova', 'Màntova']]]
];
const out = [];
F.forEach(([t, sost], i) => {
  const n = 'a' + String(i + 1).padStart(2, '0');
  let con = t; sost.forEach(([a, b]) => { con = con.replace(new RegExp('(?<![\\wÀ-ÿ])' + a + '(?![\\wÀ-ÿ])'), b); });
  out.push({ chiave: n + '-senza', gruppo: 'accenti', dove: 'prova-accenti', testo: t, lettura: t, parole: sost });
  out.push({ chiave: n + '-con', gruppo: 'accenti', dove: 'prova-accenti', testo: t, lettura: con, parole: sost });
});
fs.writeFileSync(process.argv[2], JSON.stringify(out, null, 1));
out.filter(x => x.chiave.endsWith('con')).forEach(x => console.log(x.lettura));
