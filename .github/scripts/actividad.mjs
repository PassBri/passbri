// Genera assets/actividad.svg con las contribuciones de los últimos 31 días.
// En GitHub Actions usa la API GraphQL (GITHUB_TOKEN). Localmente acepta un
// JSON {"AAAA-MM-DD": n, ...} como argumento.
import { readFileSync, writeFileSync } from "node:fs";

const USUARIO = process.env.USUARIO || "PassBri";
const DIAS = 31;

async function contribuciones() {
  if (process.argv[2]) return JSON.parse(readFileSync(process.argv[2], "utf8"));
  const q = `query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}`;
  const r = await fetch("https://api.github.com/graphql", {
    method: "POST",
    headers: { Authorization: `bearer ${process.env.GITHUB_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ query: q, variables: { u: USUARIO } }),
  });
  const j = await r.json();
  if (!j.data) throw new Error(JSON.stringify(j));
  const mapa = {};
  for (const s of j.data.user.contributionsCollection.contributionCalendar.weeks)
    for (const d of s.contributionDays) mapa[d.date] = d.contributionCount;
  return mapa;
}

const mapa = await contribuciones();
const hoy = new Date();
const dias = [];
for (let i = DIAS - 1; i >= 0; i--) {
  const f = new Date(Date.UTC(hoy.getUTCFullYear(), hoy.getUTCMonth(), hoy.getUTCDate() - i));
  const k = f.toISOString().slice(0, 10);
  dias.push({ k, n: mapa[k] || 0, d: f.getUTCDate() });
}

const W = 1200, H = 400, iz = 96, de = 56, ar = 132, ab = 64;
const max = Math.max(4, ...dias.map((x) => x.n));
const paso = Math.ceil(max / 4);
const tope = paso * 4;
const x = (i) => iz + (i * (W - iz - de)) / (DIAS - 1);
const y = (n) => H - ab - (n / tope) * (H - ar - ab);
const pts = dias.map((p, i) => [x(i), y(p.n)]);
const linea = pts.map(([a, b], i) => `${i ? "L" : "M"}${a.toFixed(1)} ${b.toFixed(1)}`).join(" ");
const area = `${linea} L${x(DIAS - 1).toFixed(1)} ${H - ab} L${iz} ${H - ab} Z`;
const total = dias.reduce((s, p) => s + p.n, 0);
const activos = dias.filter((p) => p.n > 0).length;

let rejilla = "";
for (let v = 0; v <= tope; v += paso)
  rejilla += `<line x1="${iz}" x2="${W - de}" y1="${y(v)}" y2="${y(v)}" class="r"/><text x="${iz - 10}" y="${y(v) + 4}" text-anchor="end" class="t">${v}</text>`;
const etiquetas = dias.map((p, i) => (i % 3 === 0 || i === DIAS - 1) ? `<text x="${x(i)}" y="${H - ab + 20}" text-anchor="middle" class="t">${p.d}</text>` : "").join("");
const puntos = pts.map(([a, b], i) => `<circle cx="${a.toFixed(1)}" cy="${b.toFixed(1)}" r="4.5" class="p"><title>${dias[i].k}: ${dias[i].n}</title></circle>`).join("");

const fam = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif";
const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Actividad de ${USUARIO} en GitHub: ${total} contribuciones en los últimos ${DIAS} días">
<style>text{font-family:${fam}}.t{font-size:15px;fill:#7f93b3}.r{stroke:#a9b8d0;stroke-opacity:.10}.p{fill:#ffc83d}</style>
<defs>
<radialGradient id="f" cx="15%" cy="0%" r="120%"><stop offset="0" stop-color="#13305e"/><stop offset=".5" stop-color="#0a1530"/><stop offset="1" stop-color="#05070d"/></radialGradient>
<pattern id="pt" width="28" height="28" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#3aa0ff" fill-opacity=".10"/></pattern>
<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#3aa0ff" stop-opacity=".45"/><stop offset="1" stop-color="#3aa0ff" stop-opacity="0"/></linearGradient>
<clipPath id="c"><rect width="${W}" height="${H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#c)"><rect width="${W}" height="${H}" fill="url(#f)"/><rect width="${W}" height="${H}" fill="url(#pt)"/></g>
<rect x=".75" y=".75" width="${W - 1.5}" height="${H - 1.5}" rx="22" fill="none" stroke="#3aa0ff" stroke-opacity=".3" stroke-width="1.5"/>
<path d="M62 56l6 6-6 6-6-6z" fill="#ffc83d"/><text x="80" y="68" font-size="15" letter-spacing="6" font-weight="600" fill="#ffc83d">06 · ACTIVIDAD</text>
<text x="56" y="108" font-size="30" font-weight="300" fill="#eef4ff">Contribuciones de los últimos ${DIAS} días</text>
<text x="${W - de}" y="74" text-anchor="end" font-size="40" font-weight="600" fill="#3aa0ff">${total}</text>
<text x="${W - de}" y="104" text-anchor="end" font-size="16" fill="#a9b8d0">contribuciones · ${activos} días activos</text>
${rejilla}
<path d="${area}" fill="url(#g)"/>
<path d="${linea}" fill="none" stroke="#3aa0ff" stroke-width="3" stroke-linejoin="round"/>
${puntos}${etiquetas}
</svg>
`;
writeFileSync("assets/actividad.svg", svg);
console.log(`actividad.svg: ${total} contribuciones en ${DIAS} días`);
