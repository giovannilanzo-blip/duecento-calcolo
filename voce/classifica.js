// Divisione per argomento: Nicola legge storia e guerre, F07 legge vita quotidiana. Unità = scheda, missione o lezione.
'use strict';
const fs = require('fs');
const w = s => s.trim().split(/\s+/);
const LEZ_F = w('mare_grano natura_paesaggio corte_federico');
const MIS_F = w('studium_1224 corte_sapienti castel_del_monte rotte_grano');
const D_F_PERS = w('pia_tolomei');
const A_N = w('a_usbergo a_elmo a_piastre a_sopravveste');
const F_N = w('f_scomunica');
const GL_N = w('arengo balia bando berroviere camaglio cavallata cimiero consorteria destriero fante gonfalone gonfaloniere gualdrappa guasto lega milites pavese quadrello rocca sindacato societa_armi statuto stocco vicario popolo_grasso popolo_minuto sesto');
const SIC_N = w(`s_guglielmo2 s_costanza_altavilla s_enrico6 s_federico_palermo s_pietro3 s_costanza_svevia s_procida s_mastrangelo s_alaimo s_lauria
 s_giacomo2 s_federico3 s_blasco s_filippo_taranto s_vigna s_messina s_termini s_lucera s_vespro s_communitas s_b_messina s_b_malta s_b_napoli
 s_b_falconaria s_caltabellotta s_costituzioni_melfi s_musulmani s_almogaveri s_costanza_aragona s_bianca_lancia s_salza s_taddeo s_assise_capua
 gl_vespro gl_giustiziere gl_universitas gl_parlamento_sic gl_almogavero gl_galea gl_ammiraglio gl_magna_curia gl_stratigoto gl_logoteta
 m_galea m_ammiraglio m_arsenale m_repubbliche m_genova m_embriaco m_venezia m_amalfi m_leone_foresta m_b_giglio m_b_meloria m_b_malta m_b_napoli
 m_crociata_1228 m_acri m_trapani`);
const DESC_N = w(`firenze siena pisa lucca arezzo impero angio milano bologna milite picchiere pavesaro arciere balestriere cavalleggero cavaliere
 ariete mangano trabucco carroccio feditore masnadiere balestriere_pisano gualdana cavaliere_vescovile saraceno cavaliere_francese compagnia_morte
 pavesaro_bolognese caserma balestreria scuderia torre mura porta rocca martinella coscrizione punte_ferro cotta_maglia corazza_piastre barda
 imbottitura lance_lunghe ordine_chiuso staffa tiro_mirato cavalli_frisoni scomunica ingegneri contrappeso merlatura piombatoi`);
// schede di confine: scelta e motivo (per DIVISIONE.txt)
const CONFINE = [
  ['Codice: dante', 'Nicola', 'la scheda racconta soprattutto la vita politica e militare di Dante (Campaldino, priorato, esilio)'],
  ['Codice: brunetto_latini', 'Nicola', "prevalgono l'ambasceria, Montaperti e l'esilio rispetto all'opera letteraria"],
  ['Codice: pia_tolomei', 'F07', 'personaggio letterario del Purgatorio, senza contenuto politico o militare'],
  ['Codice: a_usbergo, a_elmo, a_piastre, a_sopravveste', 'Nicola', "armature e veste da combattimento, anche se la sigla è quella dell'abbigliamento"],
  ['Codice: a_colori', 'F07', 'tinture e prezzi delle stoffe'],
  ['Codice: f_scomunica', 'Nicola', 'arma politica dei papi contro imperatori e città'],
  ['Codice: f_eresie', 'F07', 'movimenti religiosi come pratica di fede'],
  ['Codice: g_araldica', 'Nicola', 'stemmi nati per riconoscere i cavalieri in battaglia'],
  ['Glossario: ciompi', 'F07', "lavoranti dell'Arte della Lana"],
  ['Glossario: consorteria', 'Nicola', 'patto di difesa armata fra famiglie di magnati'],
  ['Glossario: popolo grasso, popolo minuto', 'Nicola', 'ceti definiti dal governo e dalle cariche pubbliche'],
  ['Glossario: sesto', 'Nicola', 'circoscrizione che elegge i priori e manda soldati'],
  ['Glossario: terziere, contrada, borgo, piviere', 'F07', 'parti della città e della campagna, senza contenuto politico'],
  ['Glossario: gualdrappa', 'Nicola', 'copertura del cavallo da guerra'],
  ['Glossario: colletta, gabella, decima, estimo, prestanza', 'F07', 'tasse e prestiti, quindi economia'],
  ['Glossario siciliano: trinacria', 'F07', 'nome della Sicilia, nessun contenuto militare'],
  ['Sicilia: s_vigna (Pier della Vigna)', 'Nicola', 'giudice e funzionario di Federico II; la poesia occupa una sola frase'],
  ['Sicilia: s_palermo', 'F07', 'città descritta per abitanti, quartieri e porto'],
  ['Sicilia: s_musulmani', 'Nicola', 'ribellione e deportazione a Lucera'],
  ['Sicilia: s_castel_del_monte, s_foggia', 'F07', 'edifici di residenza e di funzione incerta'],
  ['Mare: m_arsenale', 'Nicola', 'cantiere delle galee da guerra'],
  ['Mare: m_acri', 'Nicola', 'porto dei crociati conquistato dai mamelucchi'],
  ['Mare: m_tunisi', 'F07', 'commercio del grano e console dei mercanti'],
  ['Mare: m_leone_foresta', 'Nicola', 'nave da guerra pisana'],
  ['Mare: m_trapani', 'Nicola', 'battaglia navale e sbarco di Pietro III'],
  ['Mare: m_nave_tonda, m_taride, m_carta_nautica', 'F07', 'navi e strumenti del commercio'],
  ['Descrizioni: scuderia, cavalli_frisoni', 'Nicola', 'cavalli da guerra del Comune'],
  ['Descrizioni: ferratura, muratura', 'F07', 'mestieri del maniscalco e del muratore'],
  ['Descrizioni: scomunica', 'Nicola', 'scomunica e interdetto usati in politica'],
  ['Descrizioni: palazzo', 'F07', 'edificio civile del Comune, secondo l\'indicazione sugli edifici civili, benché sede del podestà e dei consigli'],
  ['Descrizioni: casatorre (tutte)', 'F07', 'descrizioni di edifici; quella di Firenze cita anche le società di torre dei magnati'],
  ['Descrizioni: contadino, frate, mercante, maestro', 'F07', 'mestieri e vita religiosa, anche se nel gioco sono unità'],
  ['Lezione: citta_torri', 'Nicola', 'torri dei magnati come potere e difesa'],
  ['Lezioni: frasi fisse', 'Nicola', 'istruzioni delle lezioni: restano al narratore principale'],
  ['Lezioni: mare_grano, corte_federico', 'F07', 'commercio del grano; cultura della corte'],
  ['Missioni: re_fanciullo, palermo_federico', 'Nicola', 'missioni politiche del giovane re, pur con giardini e mercato'],
  ['Missioni: castel_del_monte, studium_1224, corte_sapienti, rotte_grano', 'F07', 'falconeria, fondazione dello Studium, poeti e sapienti, commercio del grano']
];
function scheda(x) {
  const p = x.dove.split('.');
  if (x.gruppo === 'a-lezioni') return { tipo: 'lez', id: p[0] };
  if (x.gruppo === 'b-missioni') return { tipo: 'mis', id: p[1] };
  if (x.gruppo === 'e-descrizioni') return { tipo: 'desc', id: p[2] };
  return { tipo: x.gruppo === 'c-codice' ? 'reg' : 'cod', id: p[1] };
}
function voce(x) {
  const { tipo, id } = scheda(x);
  if (tipo === 'lez') return LEZ_F.includes(id) ? 'F' : 'N';
  if (tipo === 'mis') return MIS_F.includes(id) ? 'F' : 'N';
  if (tipo === 'desc') return DESC_N.includes(id) ? 'N' : 'F';
  if (tipo === 'reg') return SIC_N.includes(id) ? 'N' : 'F';
  if (/^(c|b|g|i)_/.test(id)) return 'N';
  if (/^(v|e)_/.test(id)) return 'F';
  if (/^a_/.test(id)) return A_N.includes(id) ? 'N' : 'F';
  if (/^f_/.test(id)) return F_N.includes(id) ? 'N' : 'F';
  if (/^gl_/.test(id)) return GL_N.includes(id.slice(3)) ? 'N' : 'F';
  return D_F_PERS.includes(id) ? 'F' : 'N';   // personaggi storici
}
module.exports = { voce, scheda, CONFINE };
if (require.main === module) {
  const [nic, f07, outN, outF] = process.argv.slice(2);
  const N = JSON.parse(fs.readFileSync(nic, 'utf8')), F = JSON.parse(fs.readFileSync(f07, 'utf8'));
  const byF = {}; F.forEach(x => { byF[x.chiave] = x; });
  const m = x => ({ chiave: x.chiave, gruppo: x.gruppo, dove: x.dove, testo: x.testo, lettura: x.lettura });
  const eN = [], eF = [];
  N.forEach(x => (voce(x) === 'N' ? eN.push(m(x)) : eF.push(m(byF[x.chiave]))));
  fs.writeFileSync(outN, JSON.stringify(eN)); fs.writeFileSync(outF, JSON.stringify(eF));
  const r = (L, n) => { const g = {}; L.forEach(x => { g[x.gruppo] = (g[x.gruppo] || 0) + 1; }); console.log(n, L.length, 'testi', L.reduce((a, x) => a + x.testo.length, 0), 'caratteri del gioco', L.reduce((a, x) => a + x.lettura.length, 0), 'caratteri letti', JSON.stringify(g)); };
  r(eN, 'Nicola'); r(eF, 'F07');
}
