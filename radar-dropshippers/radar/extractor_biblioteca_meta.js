// Extractor de la Biblioteca de anuncios de Meta · lo corre Claude en Chrome durante la revisión semanal.
// Uso: abrir https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=CO&q=<palabra>&search_type=keyword_unordered
// bajar hasta el final 2-3 veces y ejecutar esto. Devuelve una fila por anunciante.
(() => {
  const M = {ene:0,feb:1,mar:2,abr:3,may:4,jun:5,jul:6,ago:7,sept:8,sep:8,oct:9,nov:10,dic:11};
  const hoy = new Date();
  const g = {};
  for (const b of document.body.innerText.split(/Identificador de la biblioteca:/).slice(1)) {
    const L = b.split('\n').map(s => s.trim()).filter(s => s && s !== '\u200b');
    const m = b.match(/desde el (\d+) (\w+)\.? (\d{4})/);
    const dias = m ? Math.round((hoy - new Date(+m[3], M[m[2].toLowerCase()], +m[1])) / 864e5) : 0;
    const copias = +((b.match(/(\d+) anuncios usan/) || [])[1] || 1);
    const i = L.indexOf('Publicidad');
    const anunciante = i > 0 ? L[i - 1] : '?';
    const dominio = (L.find(s => /^[A-Z0-9.-]+\.(COM|CO|STORE|SHOP|ONLINE|NET|XYZ|LAT)(\/.*)?$/i.test(s)) || '').split('/')[0].toLowerCase();
    const x = g[anunciante] ||= {anuncios: 0, copias: 0, max: 0, min: 1e9, dominios: new Set(), texto: (L[i + 1] || '').slice(0, 60)};
    x.anuncios++; x.copias += copias; x.max = Math.max(x.max, dias); x.min = Math.min(x.min, dias);
    if (dominio) x.dominios.add(dominio === 'api.whatsapp.com' ? 'whatsapp' : dominio);
  }
  return Object.entries(g).sort((a, b) => b[1].max - a[1].max)
    .map(([a, x]) => [a, x.anuncios, x.copias, x.min + '-' + x.max + 'd', [...x.dominios].join(','), x.texto].join(' | ')).join('\n');
})();
