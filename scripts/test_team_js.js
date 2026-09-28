/* 完克配队 JS 核心逻辑验证（node 加载 index.html 内嵌脚本 + DOM stub） */
const fs = require("fs");
const vm = require("vm");

const html = fs.readFileSync(
  "C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/index.html", "utf8");
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error("未找到内嵌脚本"); process.exit(1); }

const fakeEl = {
  innerHTML: "", textContent: "", value: "",
  classList: { add(){}, remove(){}, toggle(){}, contains(){ return false; } },
  addEventListener(){}, setAttribute(){}, getAttribute(){ return null; },
  appendChild(){}, querySelectorAll(){ return []; }, querySelector(){ return null; },
  style: {}, scrollIntoView(){}, focus(){}
};
const ctx = {
  console, JSON, Math, BigInt, parseInt, isNaN, setTimeout, clearTimeout,
  localStorage: { getItem(){ return null; }, setItem(){} },
  IntersectionObserver: function(){ return { observe(){}, unobserve(){} }; },
  document: {
    addEventListener(){}, querySelectorAll(){ return []; },
    getElementById(){ return fakeEl; }, querySelector(){ return fakeEl; },
    body: fakeEl
  },
  window: null
};
ctx.window = ctx;
vm.createContext(ctx);
vm.runInContext(m[1], ctx, { filename: "index-inline.js" });

let pass = 0, fail = 0;
function chk(name, cond, extra){
  if (cond){ pass++; console.log("  ✓ " + name); }
  else { fail++; console.log("  ✗ " + name + (extra ? "  → " + extra : "")); }
}

const TM = ctx.TM;
chk("组合总数 = 73", TM.length === 73, "got " + TM.length);
const idxOf = key => { for (let i = 0; i < TM.length; i++) if (TM[i].key === key) return i; return -1; };
/* 注：JS 组合 key 按 18 属性权威顺序（飞行<草 → "飞行/草"；水<恶 → "水/恶"） */
const iCF = idxOf("飞行/草");
const iWE = idxOf("水/恶");
const iFT = idxOf("格斗/毒");
const iGD = idxOf("地面/龙");
const iSE = idxOf("钢/电");
chk("飞行/草 存在", iCF !== -1);
chk("水/恶 存在", iWE !== -1);
chk("格斗/毒 存在", iFT !== -1);
chk("地面/龙 存在", iGD !== -1);
chk("钢/电 存在", iSE !== -1);

/* 单属性段 sanity：钢/电 被地面 4x 克（地面打电=2）→ d1n 不含地面(bit4)；含妖精(bit17, 妖精打钢=0.5) */
chk("钢/电 不防御完克地面（被4x克）", iSE !== -1 && ((TM[iSE].d1n >> 4) & 1) === 0,
    TM[iSE] ? "d1n=" + TM[iSE].d1n : "no");
chk("钢/电 防御完克妖精", iSE !== -1 && ((TM[iSE].d1n >> 17) & 1) === 1,
    TM[iSE] ? "d1n=" + TM[iSE].d1n : "no");
chk("钢/电 攻击完克飞行(2x)", iSE !== -1 && ((TM[iSE].a1n >> 2) & 1) === 1,
    TM[iSE] ? "a1n=" + TM[iSE].a1n : "no");

/* 固定 3 只（草飞、水恶、格斗毒）→ 补 2 只：与 Python 无剪枝暴力一致 = 2 组无序组合
 * {地面/龙, 电/钢} 与 {地面/冰, 电/钢}（电/钢 必选，另一只二选一） */
const team = [iCF, iWE, iFT];
const covered = ctx.teamCover(team);
const all = [];
ctx.teamCollect(covered, 0, 2, [], all, team);
chk("固定3只的补位方案 = 2（无序组）", all.length === 2, "got " + all.length);
const solSets = all.map(function(p){ return [TM[p[0]].key, TM[p[1]].key].sort().join("+"); });
chk("方案含 地面/龙+钢/电", solSets.indexOf("地面/龙+钢/电") !== -1, solSets.join(" | "));
chk("方案含 地面/冰+钢/电", solSets.indexOf("地面/冰+钢/电") !== -1, solSets.join(" | "));
solSets.forEach(function(s){ console.log("    " + s); });
{
  const g = ctx.teamGaps([iCF, iWE, iFT, iGD, iSE]);
  chk("5只队伍(地龙+电钢)检测 = 完美", g.ok === true, JSON.stringify(g));
  const g2 = ctx.teamGaps([iCF, iWE, iFT, iGD, idxOf("幽灵/水")]);
  chk("换成幽灵/水则检测报缺口", g2.ok === false && (g2.dblCount > 0 || g2.atkMiss.length || g2.defMiss.length), JSON.stringify(g2));
}

/* 全量穷举：5 只方案总数应与 Python 侧 3461 一致（权威矩阵） */
console.log("  穷举 C(73,5) 校验 3461 …");
let cnt = 0;
const S1 = ctx.TM_S1, NX = ctx.TM_REQX;
for (let a = 0; a < TM.length - 4; a++)
for (let b = a + 1; b < TM.length - 3; b++)
for (let c = b + 1; c < TM.length - 2; c++)
for (let d = c + 1; d < TM.length - 1; d++)
for (let e = d + 1; e < TM.length; e++){
  let ca = TM[a].a1n | TM[b].a1n | TM[c].a1n | TM[d].a1n | TM[e].a1n;
  let cd = TM[a].d1n | TM[b].d1n | TM[c].d1n | TM[d].d1n | TM[e].d1n;
  let cx = TM[a].bx | TM[b].bx | TM[c].bx | TM[d].bx | TM[e].bx;
  if (ca === S1 && cd === S1 && cx === NX) cnt++;
}
chk("5只方案总数 = 3461（与 Python 一致）", cnt === 3461, "got " + cnt);

console.log("\n结果：通过 " + pass + "，失败 " + fail);
process.exit(fail ? 1 : 0);
