/* 导出 JS 端每个组合的 mask，供 Python 对比 */
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
const out = ctx.TM.map(m => ({ key: m.key, n36: m.n36.toString(), bx: m.bx.toString() }));
fs.writeFileSync("C:/Users/User/OneDrive/Desktop/pokemon-legends-arceus-guide/scripts/_js_masks.json", JSON.stringify(out));
console.log("exported", out.length, "combos");
