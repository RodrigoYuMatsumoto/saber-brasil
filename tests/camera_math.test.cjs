const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const context = {module:{exports:{}},globalThis:{}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../app.js"),"utf8"), context);
const {qNormalize,qMultiply,qAxis,qRotate,zoomDistance,fittedDistance} = context.module.exports;
const near = (a,b) => assert.ok(Math.abs(a-b)<1e-8, String(a)+" != "+String(b));

test("A rotação percorre polos e uma volta completa sem limitar a inclinação", () => {
  let q=[0,0,0,1];
  for(let i=0;i<100;i++) q=qNormalize(qMultiply(qAxis([1,0,0],Math.PI*2/100),q));
  const v=qRotate(q,[12,9,-4]);
  near(v[0],12);near(v[1],9);near(v[2],-4);
  const pole=qRotate(qAxis([1,0,0],Math.PI),[0,1,0]);
  near(pole[1],-1);
});

test("Rotações sucessivas preservam a distância e admitem inclinação no plano", () => {
  const q=qNormalize(qMultiply(qAxis([0,0,1],.8),qMultiply(qAxis([0,1,0],1.7),qAxis([1,0,0],2.4))));
  const point=qRotate(q,[90,120,20]);
  near(Math.hypot(...point),Math.hypot(90,120,20));
  near(Math.hypot(...q),1);
});

test("O zoom altera a distância real e respeita limites finitos", () => {
  near(zoomDistance(1000,.8),800);
  near(zoomDistance(800,1.25),1000);
  near(zoomDistance(18,.01),18);
  near(zoomDistance(40000,100),40000);
  assert.ok(600/zoomDistance(1000,.8)>600/1000);
});

test("O enquadramento mantém todos os pontos dentro da área disponível", () => {
  const points=[{x:-350,y:-380,z:40},{x:330,y:320,z:-20},{x:20,y:160,z:300}];
  const q=qNormalize(qMultiply(qAxis([0,1,0],.7),qAxis([1,0,0],-.6)));
  const distance=fittedDistance(points,q,[0,0,0],600,340,280);
  for(const point of points){
    const p=qRotate(q,[point.x,point.y,point.z]);
    const scale=600/(distance-p[2]);
    assert.ok(distance>p[2]);
    assert.ok(Math.abs(p[0]*scale)<=340);
    assert.ok(Math.abs(p[1]*scale)<=280);
  }
});

test("Zoom relativo ao enquadramento fica entre 0,25x e 24x (auditoria Grok 2026-11-12)", () => {
  const {ZOOM_MIN,ZOOM_MAX}=context.module.exports;
  near(ZOOM_MIN,.25);near(ZOOM_MAX,24);
  const base=1000;
  near(base/zoomDistance(base,1e-6,base),24);
  near(base/zoomDistance(base,1e6,base),.25);
  near(zoomDistance(base,.5,base),500);
});
