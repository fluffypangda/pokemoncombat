/* 完克配队：下拉分组 + 导入双属性优先 验证 */
const fs = require("fs");
const vm = require("vm");
const html = fs.readFileSync("C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/index.html", "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
const fakeEl = { innerHTML:"", textContent:"", value:"", classList:{add(){},remove(){},toggle(){},contains(){return false;}},
  addEventListener(){}, setAttribute(){}, getAttribute(){return null;}, appendChild(){}, querySelectorAll(){return [];},
  querySelector(){return null;}, style:{}, scrollIntoView(){}, focus(){} };
const ctx = { console, JSON, Math, BigInt, parseInt, isNaN, setTimeout, clearTimeout,
  localStorage:{ getItem(){return null;}, setItem(){} },
  IntersectionObserver: function(){ return { observe(){}, unobserve(){} }; },
  document:{ addEventListener(){}, querySelectorAll(){return [];}, getElementById(){return fakeEl;}, querySelector(){return fakeEl;}, body:fakeEl },
  window:null };
ctx.window = ctx;
vm.createContext(ctx);
vm.runInContext(m[1], ctx, { filename:"inline.js" });

let pass = 0, fail = 0;
function chk(name, cond, extra){
  if (cond){ pass++; console.log("  ✓ " + name); }
  else { fail++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); }
}
const TM = ctx.TM;

/* 1. 下拉 HTML 分组结构 */
const r = ctx.renderTeam();
const g1 = r.indexOf('optgroup label="双属性组合"');
const g2 = r.indexOf('optgroup label="单属性组合"');
chk("下拉含双属性组", g1 !== -1);
chk("下拉含单属性组", g2 !== -1);
chk("双属性组在前", g1 !== -1 && g2 !== -1 && g1 < g2);
/* 双属性选项数量 = 57，单属性 = 16（图鉴无纯飞行/纯幽灵单属性宝可梦） */
const dblOpts = (r.match(/<option value="(\d+)"[^>]*>/g) || []).length;
let cnt2 = 0, cnt1 = 0;
for (let i = 0; i < TM.length; i++){ if (TM[i].ts.length === 2) cnt2++; else cnt1++; }
chk("双属性组合 57 个", cnt2 === 57, "got " + cnt2);
chk("单属性组合 16 个", cnt1 === 16, "got " + cnt1);
chk("下拉选项总数 = 73", dblOpts === 73, "got " + dblOpts);

/* 2. 导入双属性优先：模拟已捕捉为"图鉴前12只 + 若干后面双属性"，
      前12只中双属性组合：1草/飞、3格斗/草、9水/恶；单属性：2草、4火、5火、6火、7水、8水、10一般、11一般、12电
      再加一只 地面/龙（45号圆陆鲨家族区域）模拟后面双属性。期望导入 = 双属性4只 + 1只单属性补位。 */
const captured = {};
for (let i = 1; i <= 12; i++) captured[i] = true;
captured[45] = true;   // 圆陆鲨 地面/龙（若45是圆陆鲨洗翠号，用图鉴真实查找）
// 用图鉴真名定位圆陆鲨
let landIdx = -1;
for (let i = 0; i < ctx.D.dex.length; i++){
  if (ctx.D.dex[i][2] === "圆陆鲨"){ landIdx = ctx.D.dex[i][0]; break; }
}
if (landIdx !== -1) captured[landIdx] = true;
// 追加"水水獭"（水属性、未进化）：按最终进化形态应占 水/恶（大剑鬼）坑
let otterIdx = -1;
for (let i = 0; i < ctx.D.dex.length; i++){
  if (ctx.D.dex[i][2] === "水水獭"){ otterIdx = ctx.D.dex[i][0]; break; }
}
if (otterIdx !== -1) captured[otterIdx] = true;
ctx.state.captured = captured;
ctx.state.team = [];
ctx.importCapturedTeam();
const t1 = ctx.state.team.map(i => TM[(typeof i === "number" ? i : i.ti)].key);
const dblCount = t1.filter(k => { for (let i = 0; i < TM.length; i++) if (TM[i].key === k) return TM[i].ts.length === 2; return false; }).length;
chk("导入 5 只", t1.length === 5, "got " + t1.length + " → " + t1.join("、"));
chk("导入含双属性（草/飞、格斗/草、水/恶、地面/龙）", dblCount >= 4, "双属性 " + dblCount + " → " + t1.join("、"));
chk("导入去重", t1.length === new Set(t1).size);
chk("水水獭按最终进化占水/恶坑", otterIdx !== -1 && t1.indexOf("水/恶") !== -1, "t1=" + t1.join("、"));

console.log("\n结果：通过 " + pass + "，失败 " + fail);
process.exit(fail ? 1 : 0);
