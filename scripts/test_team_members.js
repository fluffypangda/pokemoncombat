/* 完克配队：补位卡片展开 → 具体宝可梦成员（按最终进化形态归类）验证 */
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

/* 1. 成员归类：水/恶 组应含 水水獭/双刃丸/大剑鬼（进化前后都归入最终组合） */
function tiOf(key){
  for (let i = 0; i < TM.length; i++) if (TM[i].key === key) return i;
  return -1;
}
function namesOf(ti){
  return (ctx.TM_MEMBERS[ti] || []).map(i => ctx.D.dex[i][2]);
}
const we = tiOf("水/恶");
const weNames = namesOf(we);
chk("水/恶 组存在", we !== -1);
chk("水/恶 组含 水水獭", weNames.indexOf("水水獭") !== -1, weNames.join("、"));
chk("水/恶 组含 双刃丸", weNames.indexOf("双刃丸") !== -1, weNames.join("、"));
chk("水/恶 组含 大剑鬼", weNames.indexOf("大剑鬼") !== -1, weNames.join("、"));

/* 2. 格斗/草 组应含 狙射树枭（洗翠）+ 裙儿小姐（洗翠）+ 木木枭/投羽枭（进化路径） */
const ft = tiOf("格斗/草");
const ftNames = namesOf(ft);
chk("格斗/草 组存在", ft !== -1);
chk("格斗/草 组含 狙射树枭", ftNames.indexOf("狙射树枭") !== -1, ftNames.join("、"));
chk("格斗/草 组含 裙儿小姐", ftNames.indexOf("裙儿小姐") !== -1, ftNames.join("、"));
chk("格斗/草 组含 木木枭（进化路径）", ftNames.indexOf("木木枭") !== -1, ftNames.join("、"));

/* 3. 展开渲染：tmOpen 时成员行含 data-act="tMember" 与具体编号 */
ctx.state.team = [{ti: tiOf("飞行/草"), no: 1}];
ctx.state.tmOpen = ft;
const r = ctx.teamCardHtml(ft, "还有 1 种补法");
chk("展开含成员区", r.indexOf("tc-members") !== -1);
chk("展开含狙射树枭行（洗翠）", r.indexOf("狙射树枭") !== -1);
chk("成员行带 data-no", /data-act="tMember" data-i="\d+" data-no="\d+"/.test(r));
chk("含不指定直加行", r.indexOf("不指定具体宝可梦") !== -1);
/* 折叠时无成员区 */
ctx.state.tmOpen = null;
const r2 = ctx.teamCardHtml(ft, "还有 1 种补法");
chk("折叠时无成员区", r2.indexOf("tc-members") === -1);

/* 4. 槽位渲染：选了 水水獭（no=其洗翠号）应显示进化提示 */
let otterNo = -1;
for (let i = 0; i < ctx.D.dex.length; i++) if (ctx.D.dex[i][2] === "水水獭"){ otterNo = ctx.D.dex[i][0]; break; }
ctx.state.team = [{ti: we, no: otterNo}];
const rs = ctx.renderTeam();
chk("槽位显示 水水獭", rs.indexOf("水水獭") !== -1);
chk("槽位显示可进化成 大剑鬼", rs.indexOf("大剑鬼") !== -1 && rs.indexOf("可进化成") !== -1);

console.log("\n结果：通过 " + pass + "，失败 " + fail);
process.exit(fail ? 1 : 0);
