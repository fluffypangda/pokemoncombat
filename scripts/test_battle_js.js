/* 对战建议页验证（新矩阵 + 正确防御口径：对手每属性招式分别算，max<=0.5 进抗打榜） */
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
const D = ctx.D;
const TI = t => D.types.indexOf(t);
const findNo = nm => { for (let i = 0; i < D.dex.length; i++) if (D.dex[i][2] === nm) return D.dex[i][0]; return -1; };

ctx.state.captured = {};
for (const nm of ["木木枭","小磁怪","幽尾玄鱼","大钢蛇","伦琴猫"]){
  const no = findNo(nm);
  if (no !== -1) ctx.state.captured[no] = true;
}

/* ===== 对手：水/飞行 =====
 * 克制榜（攻击 >=2）：小磁怪(电 4x)、伦琴猫(电 4x)、木木枭(草2x：草打水2×草打飞行1) —— 3 只
 * 抗打榜（对手两属性招式都 <=0.5）：
 *   小磁怪(电/钢)：水招1×0.5=0.5、飞招0.5×0.5=0.25 → max 0.5 ✓ 唯一一只
 *   大钢蛇：水招0.5×2=1 ✗；木木枭：飞招1 ✗；幽尾玄鱼：飞招1 ✗；伦琴猫：水招1 ✗
 */
ctx.state.battle = { a: TI("水"), b: TI("飞行") };
let r = ctx.renderBattle();
chk("水/飞 克制榜 3 只", r.indexOf("克制榜 · 3 只") !== -1, "实际: " + (r.match(/克制榜 · (\d+) 只/) || [])[1]);
chk("克制榜含小磁怪/伦琴猫", r.indexOf("小磁怪") !== -1 && r.indexOf("伦琴猫") !== -1);
chk("水/飞 抗打榜 1 只（小磁怪）", r.indexOf("抗打榜 · 1 只") !== -1, "实际: " + (r.match(/抗打榜 · (\d+) 只/) || [])[1]);
chk("小磁怪标完美（攻4x+防0.5）", r.indexOf("完美") !== -1);
chk("抗打榜不含大钢蛇（水招1x）", r.indexOf("大钢蛇") === -1 || r.indexOf("大钢蛇") > r.indexOf("抗打榜"), "大钢蛇@index=" + r.indexOf("大钢蛇"));

/* ===== 对手：单属性水 =====
 * 克制榜（攻击>=2）：伦琴猫(电2x)、小磁怪(电2x)、木木枭(草2x) —— 3 只
 * 抗打榜（水招打我都<=0.5）：幽尾玄鱼(0.5)、小磁怪(0.5)、木木枭(0.5) —— 3 只
 */
ctx.state.battle = { a: TI("水"), b: null };
r = ctx.renderBattle();
chk("单水 克制榜 3 只（电/草）", r.indexOf("克制榜 · 3 只") !== -1, "实际: " + (r.match(/克制榜 · (\d+) 只/) || [])[1]);
chk("单水 抗打榜 3 只", r.indexOf("抗打榜 · 3 只") !== -1, "实际: " + (r.match(/抗打榜 · (\d+) 只/) || [])[1]);

/* ===== 对手：单属性草 =====
 * 克制榜：木木枭(飞2x) 1 只
 * 抗打榜（草招打我都<=0.5）：木木枭(0.5)、小磁怪(0.5) —— 2 只（幽尾玄鱼被草2x、大钢蛇被草2x、伦琴猫草1x）
 */
ctx.state.battle = { a: TI("草"), b: null };
r = ctx.renderBattle();
chk("单草 克制榜 1 只（木木枭飞2x）", r.indexOf("克制榜 · 1 只") !== -1, "实际: " + (r.match(/克制榜 · (\d+) 只/) || [])[1]);
chk("单草 抗打榜 2 只（木木枭/小磁怪）", r.indexOf("抗打榜 · 2 只") !== -1, "实际: " + (r.match(/抗打榜 · (\d+) 只/) || [])[1]);

/* ===== 无已捕捉 ===== */
ctx.state.captured = {};
ctx.state.battle = { a: TI("火"), b: null };
r = ctx.renderBattle();
chk("无已捕捉时提示", r.indexOf("还没有标记任何") !== -1);

console.log("\n结果：通过 " + pass + "，失败 " + fail);
process.exit(fail ? 1 : 0);
