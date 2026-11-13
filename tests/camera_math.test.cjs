const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const context = {module:{exports:{}},globalThis:{}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname,"../app.js"),"utf8"), context);
const {qNormalize,qMultiply,qAxis,qRotate,zoomDistance,anchorPan,orbitTarget,fittedDistance} = context.module.exports;
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
  near(zoomDistance(18,.01),1000/24);
  near(zoomDistance(40000,100),4000);
  near(zoomDistance(500,.0001,2400),100);
  near(zoomDistance(500,1000,2400),9600);
  assert.ok(600/zoomDistance(1000,.8)>600/1000);
});

test("A roda mantém o ponto sob o cursor na projeção perspectiva", () => {
  const center=[845,400],pan=[37,-18],anchor=[990,315],focal=650,depth=124,oldDistance=1200,newDistance=600;
  const point=[(anchor[0]-center[0]-pan[0])*(oldDistance-depth)/focal,(anchor[1]-center[1]-pan[1])*(oldDistance-depth)/focal];
  const moved=anchorPan(pan,center,anchor,oldDistance,newDistance,depth);
  near(center[0]+moved[0]+point[0]*focal/(newDistance-depth),anchor[0]);
  near(center[1]+moved[1]+point[1]*focal/(newDistance-depth),anchor[1]);
});

test("A órbita livre usa o nó selecionado como pivô sem deslocar sua projeção", () => {
  const oldQ=qNormalize(qMultiply(qAxis([0,1,0],.6),qAxis([1,0,0],-.3)));
  const pivot=[137,200,-68],target=[-12,40,23];
  const before=qRotate(oldQ,pivot.map((v,i)=>v-target[i]));
  for(const angle of [Math.PI/2,Math.PI,Math.PI*1.6,Math.PI*2]){
    const next=qNormalize(qMultiply(qMultiply(qAxis([0,0,1],.7),qAxis([1,0,0],angle)),oldQ));
    const moved=orbitTarget(oldQ,next,target,pivot);
    const after=qRotate(next,pivot.map((v,i)=>v-moved[i]));
    after.forEach((v,i)=>near(v,before[i]));
  }
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
