/* 推荐排行 JS 逻辑验证 */
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
const idxOf = key => { for (let i = 0; i < TM.length; i++) if (TM[i].key === key) return i; return -1; };

/* 弱点 mask 抽验（D.types 序：0一般 1格斗 2飞行 3毒 4地面 5岩石 6虫 7幽灵 8钢 9火 10水 11草 12电 13超能 14冰 15龙 16恶 17妖精）
 * 权威矩阵口径：电打钢=0.5、水打钢=0.5、钢打毒/草/超/龙/恶=1 等 */
const iSE = idxOf("钢/电");
chk("钢/电 存在", iSE !== -1);
if (iSE !== -1){
  const w = TM[iSE].wn;
  chk("钢/电 弱点 = 格斗/地面/火（3种）", (w >> 1 & 1) === 1 && (w >> 4 & 1) === 1 && (w >> 9 & 1) === 1 && ctx.popcN(w) === 3,
      "wn=" + w + " popc=" + ctx.popcN(w));
}
const iGW = idxOf("幽灵/水");
chk("幽灵/水 存在", iGW !== -1);
if (iGW !== -1){
  const w = TM[iGW].wn;
  const want = (w >> 7 & 1) === 1 && (w >> 11 & 1) === 1 && (w >> 12 & 1) === 1 && (w >> 13 & 1) === 1 && (w >> 16 & 1) === 1 && ctx.popcN(w) === 5;
  chk("幽灵/水 弱点 = 幽灵/草/电/超能力/恶（5种）", want, "wn=" + w + " popc=" + ctx.popcN(w));
}
/* 大钢蛇 地面/钢：格斗2x、地面2x、火2x（水0.5×2=1 不弱） → 弱点=格斗/地面/火 3 种 */
const iGS = idxOf("地面/钢");
chk("地面/钢 存在", iGS !== -1);
if (iGS !== -1){
  const w = TM[iGS].wn;
  chk("地面/钢 弱点 = 格斗/地面/火（3种）", (w >> 1 & 1) === 1 && (w >> 4 & 1) === 1 && (w >> 9 & 1) === 1 && ctx.popcN(w) === 3,
      "wn=" + w + " popc=" + ctx.popcN(w));
}

/* 榜单数据导出（双属性组合：弱点数/克制数/综合），与 Python 对比 */
const rows = [];
for (let i = 0; i < TM.length; i++){
  if (TM[i].ts.length !== 2) continue;
  rows.push({ key: TM[i].key, wn: ctx.popcN(TM[i].wn), an: ctx.popcN(TM[i].a1n) });
}
fs.writeFileSync("C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/scripts/_rank_js.json",
  JSON.stringify(rows), "utf8");
chk("双属性组合数 = 57", rows.length === 57, "got " + rows.length);
console.log("导出 " + rows.length + " 条榜单数据");
console.log("\n结果：通过 " + pass + "，失败 " + fail);
process.exit(fail ? 1 : 0);
