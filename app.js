/* Saber Brasil. Interface local, sem rastreamento nem serviços de tradução obrigatórios. */
(function (root) {
  "use strict";
  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const qNormalize = q => { const n = Math.hypot(...q) || 1; return q.map(v => v / n); };
  const qMultiply = (a,b) => [a[3]*b[0]+a[0]*b[3]+a[1]*b[2]-a[2]*b[1],a[3]*b[1]-a[0]*b[2]+a[1]*b[3]+a[2]*b[0],a[3]*b[2]+a[0]*b[1]-a[1]*b[0]+a[2]*b[3],a[3]*b[3]-a[0]*b[0]-a[1]*b[1]-a[2]*b[2]];
  const qAxis = (axis,angle) => { const s=Math.sin(angle/2); return [axis[0]*s,axis[1]*s,axis[2]*s,Math.cos(angle/2)]; };
  const qRotate = (q,v) => { const p=qMultiply(qMultiply(q,[v[0],v[1],v[2],0]),[-q[0],-q[1],-q[2],q[3]]); return p.slice(0,3); };
  const zoomDistance = (distance,factor) => clamp(distance*factor,18,40000);
  const fittedDistance = (points,q,target,focal,halfWidth,halfHeight) => {
    let needed=120;
    for (const p of points) {
      const r=qRotate(q,[p.x-target[0],p.y-target[1],p.z-target[2]]);
      needed=Math.max(needed,r[2]+Math.max(Math.abs(r[0])*focal/Math.max(20,halfWidth),Math.abs(r[1])*focal/Math.max(20,halfHeight))*1.16);
    }
    return clamp(needed,120,40000);
  };
  const math=Object.freeze({qNormalize,qMultiply,qAxis,qRotate,zoomDistance,fittedDistance});
  if (typeof module === "object" && module.exports) { module.exports=math; return; }
  root.SaberCameraMath=math;
  const $=id=>document.getElementById(id);
  const normalize=v=>String(v??"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
  const esc=v=>String(v??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
  const safeUrl=v=>{try{const u=new URL(v);return ["https:","http:"].includes(u.protocol)?u.href:null;}catch{return null;}};
  const initialQ=()=>qNormalize(qMultiply(qAxis([0,1,0],.6),qAxis([1,0,0],-.28)));
  const state={topics:[],byId:new Map(),edges:[],next:new Map(),subjects:[],subjectLabels:{},active:new Set(),filtered:[],rendered:[],visibleIds:new Set(),selected:null,lineage:new Set(),nextIds:new Set(),query:"",grade:"all",system:"all",origin:"all",view:"graph",listLimit:60,lang:"pt-BR",locales:{},translations:{},autoTranslations:new Map(),autoReasons:new Map(),translators:new Map(),history:[],hover:null,loaded:false,missing:[],paused:matchMedia("(prefers-reduced-motion: reduce)").matches,camera:{q:initialQ(),distance:1400,baseDistance:1400,target:[0,0,0],pan:[0,0],focused:null},pointers:new Map(),gesture:null,lastFrame:0};
  const colors={portugues:"#f5d352",matematica:"#4b94eb",ciencias:"#68cda4",historia:"#e7c976",geografia:"#96dab3",arte:"#c5bf7e","educacao-fisica":"#1eab78",ingles:"#b0cef5","ensino-religioso":"#e6e4c7",computacao:"#677fe0","desenvolvimento-pessoal-social":"#86bda9","habilidades-para-vida":"#a9c89a","aprender-a-aprender":"#d8cc88",frances:"#91a8d1",japones:"#e9c889",chines:"#8fc5bd","estudos-sociais":"#7abdb4","educacao-moral":"#d2d58a","economia-domestica":"#a3bca7",tecnologia:"#709be0","trabalho-pratico":"#b9c384","estudos-integrados":"#97b3d4"};
  const canvas=$("graph"),ctx=canvas.getContext("2d",{alpha:false});
  let width=0,height=0,dpr=1,projected=[],renderOrder=[],raf=0;
  const t=(key,args={})=>{
    const actual=(args.n===1||args.n==="1")&&state.locales[state.lang]?.[key+"One"]?key+"One":key;
    let text=state.locales[state.lang]?.[actual]??state.locales["pt-BR"]?.[actual]??key;
    for(const [k,v] of Object.entries(args))text=text.replaceAll("{"+k+"}",String(v));
    return text;
  };
  const number=n=>new Intl.NumberFormat(state.lang).format(n);
  const announce=text=>{$("announcements").textContent=text;};
  const nativeLanguage=lang=>{try{return new Intl.DisplayNames([state.lang],{type:"language"}).of(lang)||lang;}catch{return lang;}};
  const subjectName=id=>state.locales[state.lang]?.[id]||state.subjectLabels[id]?.translations?.[state.lang]||state.subjectLabels[id]?.name||id.replaceAll("-"," ");
  const topicOrigin=topic=>topic.origin.length?topic.origin.map(t).join(" · "):t("unmappedOrigin");
  const placementIsExplicit=p=>["source-explicit","source-band"].includes(p.certainty);
  const placements=topic=>{
    const listed=Array.isArray(topic.schoolPlacements)?topic.schoolPlacements.filter(placementIsExplicit):[];
    if(listed.length||!topic.origin.includes("BR"))return listed;
    if(!Number.isInteger(topic.gradeMin)||!Number.isInteger(topic.gradeMax))return [];
    return [{system:"BR",years:Array.from({length:topic.gradeMax-topic.gradeMin+1},(_,i)=>topic.gradeMin+i),framework:"BNCC",certainty:topic.gradeMin===topic.gradeMax?"source-explicit":"source-band"}];
  };
  function translationRecord(topic,lang=state.lang){
    const automatic=state.autoTranslations.get(lang+"|"+topic.id);
    if(automatic)return automatic;
    const own=topic.translations?.[lang]||state.translations[topic.id]?.[lang];
    const name=topic.translatedNames?.[lang],description=topic.translatedDescriptions?.[lang];
    const intrinsic={};
    if(typeof name==="string")intrinsic.name=name;
    if(typeof description==="string")intrinsic.description=description;
    if(own&&typeof own==="object")return {...intrinsic,...own};
    return Object.keys(intrinsic).length?intrinsic:null;
  }
  function topicText(topic,field){
    const record=translationRecord(topic);
    return String(record?.[field]??topic[field]??"");
  }
  function hasTranslation(topic,field="description"){
    return Boolean(translationRecord(topic)?.[field])||languageCode(topic.language)===languageCode(state.lang);
  }
  const languageCode=code=>code==="pt-BR"?"pt":code==="zh-Hans"?"zh":code||"en";
  function yearLabel(system,year){
    if(system==="US")return year===0?(state.lang==="ja"?"幼稚園 K":state.lang==="zh-Hant"?"幼稚園 K":"Kindergarten (K)"):(state.lang==="pt-BR"?"Grade "+year:state.lang==="ja"?year+"年生":state.lang==="zh-Hant"?year+" 年級":"Grade "+year);
    if(system==="GB-ENG")return state.lang==="pt-BR"?"Year "+year:state.lang==="ja"?"Year "+year:state.lang==="zh-Hant"?"Year "+year:"Year "+year;
    if(system==="JP")return state.lang==="ja"?(year<=6?"小学"+year+"年":"中学"+(year-6)+"年"):state.lang==="zh-Hant"?(year<=6?"小學 "+year+" 年級":"中學 "+(year-6)+" 年級"):state.lang==="en"?(year<=6?"Elementary "+year:"Lower secondary "+(year-6)):(year<=6?year+"º ano primário":(year-6)+"º ano secundário");
    if(system==="CN")return state.lang==="zh-Hant"?(year<=6?"小學 "+year+" 年級":"初中 "+(year-6)+" 年級"):state.lang==="ja"?(year<=6?"小学"+year+"年":"初中"+(year-6)+"年"):state.lang==="en"?(year<=6?"Primary "+year:"Junior secondary "+(year-6)):(year<=6?year+"º ano primário":(year-6)+"º ano secundário");
    return state.lang==="pt-BR"?year+"º ano":state.lang==="en"?"Year "+year:year+"年"+(state.lang==="zh-Hant"?"級":"生");
  }
  function formatPlacement(p){
    const years=[...new Set(p.years||[])].sort((a,b)=>a-b);
    if(!years.length)return t("placementNone");
    const band=years.length>1?yearLabel(p.system,years[0])+" - "+yearLabel(p.system,years.at(-1)):yearLabel(p.system,years[0]);
    return t(p.system)+" · "+band+(p.certainty==="source-band"?" · "+t("band"):"");
  }
  function fmtGrade(topic){
    const ps=placements(topic);
    const selected=state.system!=="all"?ps.filter(p=>p.system===state.system):ps;
    const unique=[...new Set(selected.map(formatPlacement))];
    return unique.slice(0,2).join(" / ")||t("placementNone");
  }
  function applyLanguage(){
    document.documentElement.lang=state.lang;
    document.title=t("pageTitle");
    $("language").value=state.lang;
    document.querySelectorAll("[data-i18n]").forEach(el=>el.textContent=t(el.dataset.i18n));
    document.querySelectorAll("[data-i18n-html]").forEach(el=>el.innerHTML=t(el.dataset.i18nHtml));
    $("search").placeholder=t("searchPlaceholder");$("search").setAttribute("aria-label",t("searchLabel"));
    for(const [id,key] of Object.entries({"language":"language","school-system":"schoolSystem","grade":"grade","origin":"origin","graph-view":"graphView","list-view":"listView","detail-close":"closeConcept","about-close":"closeAbout","zoom-in":"zoomIn","zoom-out":"zoomOut","focus-topic":"focusTopic","fit-all":"fitAll","show-details":"showDetails","reset-camera":"resetCamera","roll-left":"rollLeft","roll-right":"rollRight"})){
      $(id).setAttribute("aria-label",t(key));$(id).title=t(key);
    }
    canvas.setAttribute("aria-label",t("graphAria"));
    document.querySelector(".explore-controls").setAttribute("aria-label",t("exploreMap"));
    document.querySelector(".legend").setAttribute("aria-label",t("filterSubjects"));
    const school=$("school-system");
    for(const option of school.options)option.textContent=option.value==="all"?t("allSystems"):option.value==="US"?t("usSystem"):option.value==="GB-ENG"?t("englandSystem"):t(option.value);
    document.querySelector('a[href="docs/Consenso_Taxonomias.md"]').textContent=t("consensusDoc")+" ↗";
    document.querySelector('a[href="docs/Curriculos_Japao_China.md"]').textContent=t("eastAsiaDoc")+" ↗";
    for(const option of $("origin").options)option.textContent=option.value==="all"?t("allOrigins"):option.value==="other"?t("otherOrigins"):option.value==="unmapped"?t("unmappedOrigin"):t(option.value);
    updateGradeOptions();updateTotals();updateRotate();buildSubjects();updateVisibleContext();updateSearch();
    if(state.view==="list")renderList();
    if(state.selected)renderDetail();
    $("graph-status").textContent=state.missing.length?t("missingExtra"):t("localData");
    if(state.loaded)resize();
    announce(t("results",{n:number(state.filtered.length)}));
  }
  function updateTotals(){
    $("hero-description").innerHTML=t("heroDescription",{topics:'<span id="total-concepts">'+number(state.topics.length)+"</span>",links:'<span id="total-links">'+number(state.edges.length)+"</span>"});
  }
  async function loadJson(path,required){
    try{const response=await fetch(path);if(!response.ok)throw new Error(String(response.status));return await response.json();}
    catch(error){if(required)throw error;state.missing.push(path);return {};}
  }
  async function loadData(){
    try{
      let {brazil,international,eastAsia,translations,locales}=window.SABER_DATA||{};
      if(!brazil||!international){
        [brazil,international,eastAsia,translations,locales]=await Promise.all([loadJson("data/brazil_topics.json",true),loadJson("data/international.json",true),loadJson("data/east_asia.json",false),loadJson("data/translations.json",false),loadJson("assets/locales.json",true)]);
      }
      state.locales=locales?.locales||locales||{};
      state.translations=translations?.topics||{};
      const desired=new URLSearchParams(location.search).get("lang");
      state.lang=state.locales[desired]?desired:"pt-BR";
      const datasets=[brazil,international,eastAsia].filter(Boolean);
      state.topics=datasets.flatMap(d=>d.topics||[]).map((raw,index)=>{
        const topic={...raw,id:String(raw.id),name:String(raw.name||raw.id),description:String(raw.description||""),domain:String(raw.domain||""),subject:String(raw.subject),origin:Array.isArray(raw.origin)?raw.origin:[],standards:Array.isArray(raw.standards)?raw.standards:[],prerequisites:Array.isArray(raw.prerequisites)?raw.prerequisites:[],index};
        const allNames=Object.values(state.translations[topic.id]||{}).flatMap(r=>typeof r==="object"?[r.name,r.description,r.domain]:[r]);
        topic.searchText=normalize([topic.name,topic.description,topic.domain,...allNames,...Object.values(topic.translatedNames||{}),...topic.standards.flatMap(s=>[s.code,s.sourceCodeLiteral])].join(" "));
        topic.color=colors[topic.subject]||"#a7c6be";
        return topic;
      });
      state.byId=new Map(state.topics.map(topic=>[topic.id,topic]));
      for(const d of datasets)for(const s of d.subjects||[])if(s.id)state.subjectLabels[s.id]=s;
      const priority=["portugues","matematica","ciencias","historia","geografia","arte","educacao-fisica","ingles","ensino-religioso","computacao","japones","chines"];
      state.subjects=[...new Set(state.topics.map(topic=>topic.subject))].sort((a,b)=>(priority.indexOf(a)<0?99:priority.indexOf(a))-(priority.indexOf(b)<0?99:priority.indexOf(b))||a.localeCompare(b));
      state.active=new Set(state.subjects);
      for(const topic of state.topics)for(const pre of topic.prerequisites){
        if(!state.byId.has(pre.id)||pre.id===topic.id)continue;
        const edge={from:pre.id,to:topic.id,reason:pre.reason||"",status:pre.status||"editorial",relation:pre.relation||"pre-requisito"};
        state.edges.push(edge);
        if(!state.next.has(pre.id))state.next.set(pre.id,[]);
        state.next.get(pre.id).push({topic,reason:pre.reason||"",status:edge.status,relation:edge.relation});
      }
      makePositions();state.loaded=true;applyLanguage();applyFilters(true);
      const initialId=decodeURIComponent(location.hash.slice(1));if(state.byId.has(initialId))selectTopic(initialId);
      if(!ctx)setView("list");
      Object.defineProperty(window,"__SABER_TEST__",{configurable:true,value:Object.freeze({
        getSummary:()=>({topicCount:state.topics.length,edgeCount:state.edges.length,visibleCount:state.rendered.length,filteredCount:state.filtered.length,contextCount:state.rendered.length-state.filtered.length,selected:state.selected?.id||null,subjects:state.subjects.length,activeSubjects:state.active.size,view:state.view,paused:state.paused,language:state.lang,schoolSystem:state.system,grade:state.grade,zoom:state.camera.baseDistance/state.camera.distance,camera:cameraSnapshot()}),
        getVisibleIds:()=>state.rendered.map(topic=>topic.id),getFilteredIds:()=>state.filtered.map(topic=>topic.id),
        getSelected:()=>state.selected?JSON.parse(JSON.stringify({id:state.selected.id,prerequisites:state.selected.prerequisites,placements:placements(state.selected)})):null
      })});
      announce(t("found",{n:number(state.topics.length)}));
    }catch(error){
      console.error("Saber Brasil:",error);$("load-error").hidden=false;$("load-error").textContent=t("loadError");$("graph-status").textContent=t("loadError");
    }
  }
  function hash(value){let h=2166136261;for(let i=0;i<value.length;i++){h^=value.charCodeAt(i);h=Math.imul(h,16777619);}return (h>>>0)/4294967295;}
  function makePositions(){
    state.topics.forEach(topic=>{
      const ranges=placements(topic).flatMap(p=>p.years||[]).filter(n=>n>=1&&n<=9);
      const grade=ranges.length?(Math.min(...ranges)+Math.max(...ranges))/2:(Number(topic.gradeMin||1)+Number(topic.gradeMax||topic.gradeMin||1))/2;
      const p=clamp((grade-1)/8*.8+hash(topic.id+":height")*.2,.015,.985);
      const radius=(30+p*340)*(.45+hash(topic.id+":r")*.55);
      const angle=state.subjects.indexOf(topic.subject)/state.subjects.length*Math.PI*2+(hash(topic.id+":a")-.5)*2.8+p*2.8;
      topic.x=Math.cos(angle)*radius;topic.y=(.5-p)*760;topic.z=Math.sin(angle)*radius;topic.radius=2.3+hash(topic.id+":size")*2.4;
    });
  }
  function buildSubjects(){
    if(!state.loaded)return;
    const counts=new Map();state.topics.forEach(topic=>counts.set(topic.subject,(counts.get(topic.subject)||0)+1));
    $("subjects").innerHTML=state.subjects.map(id=>'<button class="subject-chip" data-subject="'+esc(id)+'" aria-pressed="'+state.active.has(id)+'" title="'+esc(subjectName(id))+'" style="--subject-color:'+(colors[id]||"#a7c6be")+'"><span class="dot" aria-hidden="true"></span><span class="subject-label">'+esc(subjectName(id))+'</span><span class="subject-count">'+number(counts.get(id))+"</span></button>").join("");
  }
  function updateGradeOptions(){
    const years=[...new Set(state.topics.flatMap(topic=>placements(topic).filter(p=>p.system===state.system).flatMap(p=>p.years||[])))].sort((a,b)=>a-b);
    $("grade").innerHTML='<option value="all">'+esc(t("allGrades"))+"</option>"+years.map(year=>'<option value="'+year+'">'+esc(yearLabel(state.system,year))+"</option>").join("");
    if(state.grade!=="all"&&!years.includes(Number(state.grade)))state.grade="all";
    $("grade").value=state.grade;$("grade").disabled=state.system==="all";$("grade").title=state.system==="all"?t("chooseSystem"):t("systemNote");
  }
  function matchesFilters(topic){
    if(!state.active.has(topic.subject))return false;
    if(state.system!=="all"){
      const ps=placements(topic).filter(p=>p.system===state.system);
      if(!ps.length)return false;
      if(state.grade!=="all"&&!ps.some(p=>(p.years||[]).includes(Number(state.grade))))return false;
    }
    if(state.origin==="unmapped"&&topic.origin.length)return false;
    if(state.origin==="other"&&!topic.origin.some(code=>!["BR","US","GB-ENG","JP","CN","AU","CA"].includes(code)))return false;
    if(!["all","other","unmapped"].includes(state.origin)&&!topic.origin.includes(state.origin))return false;
    return !state.query||state.query.split(/\s+/).filter(Boolean).every(part=>topic.searchText.includes(part));
  }
  function applyFilters(fit=false){
    state.filtered=state.topics.filter(matchesFilters);state.listLimit=60;
    if(state.selected&&!state.filtered.some(topic=>topic.id===state.selected.id))clearSelection(false);
    updateVisibleContext();updateSearch();if(state.view==="list")renderList();
    if(fit)fitGraph(false);scheduleFrame();
  }
  function updateVisibleContext(){
    state.rendered=state.filtered.slice();state.visibleIds=new Set(state.filtered.map(topic=>topic.id));
    if(state.selected)for(const id of [state.selected.id,...state.lineage,...state.nextIds]){
      if(state.visibleIds.has(id))continue;const topic=state.byId.get(id);if(topic){state.rendered.push(topic);state.visibleIds.add(id);}
    }
    $("visible-count").textContent=t("visible",{n:number(state.filtered.length)})+(state.rendered.length>state.filtered.length?t("context",{n:number(state.rendered.length-state.filtered.length)}):"");
    $("empty").hidden=state.rendered.length>0;
    $("focus-topic").disabled=!state.selected;$("show-details").hidden=!state.selected;
    scheduleFrame();
  }
  function clearFilters(){
    clearSelection(false);state.query="";state.grade="all";state.system="all";state.origin="all";state.active=new Set(state.subjects);
    $("search").value="";$("school-system").value="all";$("origin").value="all";updateGradeOptions();buildSubjects();applyFilters(true);announce(t("filterCleared"));
  }
  function updateSearch(){
    if(!state.query||state.view==="list"){$("search-results").hidden=true;return;}
    const matches=state.filtered.slice().sort((a,b)=>Number(normalize(topicText(b,"name")).startsWith(state.query))-Number(normalize(topicText(a,"name")).startsWith(state.query))).slice(0,8);
    $("search-results").innerHTML=matches.map(topic=>'<button class="search-result" data-topic="'+esc(topic.id)+'"><strong>'+esc(topicText(topic,"name"))+'</strong><small><span class="result-subject">'+esc(subjectName(topic.subject))+"</span> · "+esc(fmtGrade(topic))+"</small></button>").join("")+'<p class="search-note">'+esc(t("results",{n:number(state.filtered.length)}))+(state.filtered.length>8?" · "+esc(t("moreResults")):"")+"</p>";
    $("search-results").hidden=false;
  }
  function setView(view){
    state.view=view;$("app").dataset.view=view;$("list-panel").hidden=view!=="list";
    $("graph-view").setAttribute("aria-pressed",String(view==="graph"));$("list-view").setAttribute("aria-pressed",String(view==="list"));$("search-results").hidden=true;
    if(view==="list"){renderList();$("results").focus({preventScroll:true});}else scheduleFrame();
  }
  function renderList(){
    $("list-count").textContent=t("found",{n:number(state.filtered.length)});
    $("results").innerHTML=state.filtered.slice(0,state.listLimit).map(topic=>'<button class="topic-row" data-topic="'+esc(topic.id)+'" style="--subject-color:'+topic.color+'"><span><strong>'+esc(topicText(topic,"name"))+"</strong><small>"+esc(subjectName(topic.subject))+" · "+esc(fmtGrade(topic))+"<br>"+esc(topicOrigin(topic))+"</small></span><span class=\"row-arrow\" aria-hidden=\"true\">↗</span></button>").join("");
    $("load-more").hidden=state.listLimit>=state.filtered.length;
  }
  function getAncestors(topic){
    const found=new Set(),pending=[topic];
    while(pending.length){const current=pending.pop();for(const pre of current.prerequisites){if(found.has(pre.id)||pre.id===topic.id)continue;const p=state.byId.get(pre.id);if(p){found.add(pre.id);pending.push(p);}}}
    return found;
  }
  function selectTopic(id,remember=true){
    const topic=state.byId.get(id);if(!topic)return;
    if(remember&&state.selected&&state.selected.id!==id)state.history.push(state.selected.id);
    state.selected=topic;state.lineage=getAncestors(topic);state.nextIds=new Set((state.next.get(id)||[]).map(x=>x.topic.id));
    updateVisibleContext();state.hover=null;$("tooltip").hidden=true;$("search-results").hidden=true;renderDetail();$("detail").hidden=false;
    try{history.replaceState(null,"",location.pathname+location.search+"#"+encodeURIComponent(id));}catch{}
    announce(topicText(topic,"name"));scheduleFrame();
  }
  function dependencyHtml(items,isNext=false,composition=false){
    if(!items.length)return '<p class="muted">'+esc(t(isNext?"noNext":"noPrerequisites"))+"</p>";
    return items.map(item=>{
      const topic=isNext?item.topic:state.byId.get(item.id);if(!topic)return "";
      const reason=state.autoReasons.get(state.lang+"|"+state.selected.id+"|"+topic.id)||item.reason||"";
      return '<button class="dependency-item" data-topic="'+esc(topic.id)+'"><span aria-hidden="true">'+(composition?"◇":isNext?"↗":"↙")+"</span><span><strong>"+esc(topicText(topic,"name"))+"</strong><small>"+esc(reason)+"</small></span></button>";
    }).join("");
  }
  function detailSection(title,items,isNext=false,composition=false){return '<div class="detail-section"><h3>'+esc(t(title))+" <span>"+number(items.length)+"</span></h3>"+dependencyHtml(items,isNext,composition)+"</div>";}
  function renderDetail(){
    const topic=state.selected;if(!topic)return;
    const incoming=topic.prerequisites.filter(p=>state.byId.has(p.id)),parts=incoming.filter(p=>p.relation==="parte-da-habilidade"),pres=incoming.filter(p=>p.relation!=="parte-da-habilidade");
    const outgoing=state.next.get(topic.id)||[],next=outgoing.filter(p=>p.relation!=="parte-da-habilidade"),related=outgoing.filter(p=>p.relation==="parte-da-habilidade");
    const parent=state.byId.get(topic.parentId),record=translationRecord(topic);
    if(parent&&!related.some(p=>p.topic.id===parent.id))related.push({topic:parent,relation:"parte-da-habilidade",reason:""});
    const name=topicText(topic,"name"),desc=topicText(topic,"description"),domain=topicText(topic,"domain");
    const kind=t(topic.kind==="habilidade"?"curricularSkill":topic.kind==="microtopico"?"microtopic":"taxonomyConcept");
    const status=topic.origin.includes("BR")?(topic.alignmentStatus==="verified"?t("referenceVerified"):t("referenceProposed")):t("noBncc");
    const translationMissing=!hasTranslation(topic);
    const languageNote=record?'<p class="translation-note">'+esc(t(record._automatic?"automaticTranslation":"editorialTranslation"))+"</p>":"";
    const missingNote=translationMissing?'<p class="translation-note">'+esc(t("translationPending"))+" "+esc(t("sourceText",{language:nativeLanguage(topic.language||"en")}))+'</p><button id="translate-native" class="small-button">'+esc(t("translateConcept"))+'</button><p id="translate-status" class="muted" role="status"></p>':"";
    const sourceNotes=[topic.sourceFormattingNote,...topic.standards.flatMap(s=>[s.normalizationNote,s.sourceCodeLiteral&&s.sourceCodeLiteral!==s.code?s.sourceCodeLiteral+" → "+s.code:""])].filter(Boolean);
    const notes=sourceNotes.length?'<p class="source-note">'+sourceNotes.map(esc).join("<br>")+"</p>":"";
    const sourceHtml=topic.standards.length?topic.standards.map(s=>{
      const url=safeUrl(s.url);const code=s.sourceCodeLiteral||s.code||s.sourceSection||s.framework||"";
      return '<div class="standard">'+(url?'<a href="'+esc(url)+'" target="_blank" rel="noopener noreferrer">'+esc(code)+" ↗</a>":"<code>"+esc(code)+"</code>")+"<p>"+esc(s.framework||"")+" · "+esc(t(s.verified?"officialSource":"sourceAlignment"))+"</p>"+(s.description?"<p lang=\""+esc(s.originalLanguage||topic.language||"en")+"\">"+esc(s.description)+"</p>":"")+"</div>";
    }).join(""):'<p class="muted">'+esc(t("noReference"))+"</p>";
    $("detail-content").innerHTML='<p class="detail-subject" style="--subject-color:'+topic.color+'">'+esc(subjectName(topic.subject))+(domain?" · "+esc(domain):"")+'</p><h2 id="detail-title">'+esc(name)+'</h2><p class="detail-description">'+esc(desc)+'</p><div class="badges"><span class="badge">'+esc(kind)+'</span><span class="badge br">'+esc(topicOrigin(topic))+'</span><span class="badge">'+esc(status)+'</span></div><p class="placement-detail">'+esc(fmtGrade(topic))+"</p>"+languageNote+missingNote+notes+(parent?'<p class="muted">'+esc(t("partOf",{code:parent.standards[0]?.sourceCodeLiteral||parent.standards[0]?.code||topicText(parent,"name")}))+"</p>":"")+(parts.length?detailSection("parts",parts,false,true)+'<p class="muted">'+esc(t("partsNote"))+"</p>":"")+detailSection(topic.origin.includes("BR")||topic.origin.includes("JP")||topic.origin.includes("CN")?"proposedPrerequisites":"sourcePrerequisites",pres)+detailSection("next",next,true)+(related.length?detailSection("relatedSkills",related,true,true):"")+'<div class="detail-section"><h3>'+esc(t("references"))+" <span>"+number(topic.standards.length)+"</span></h3>"+sourceHtml+'</div><p class="editorial-note">'+esc(t("relatedCount",{n:number(new Set([...state.lineage,...state.nextIds]).size)}))+"</p>";
  }
  function clearSelection(update=true){
    state.selected=null;state.lineage.clear();state.nextIds.clear();state.history=[];state.camera.focused=null;$("detail").hidden=true;
    try{history.replaceState(null,"",location.pathname+location.search);}catch{}
    if(update)updateVisibleContext();
  }
  function viewport(){
    const mobile=width<=760,controls=document.querySelector(".explore-controls"),controlsBottom=controls.offsetTop+controls.offsetHeight;
    if(mobile){
      const legendTop=document.querySelector(".legend").offsetTop;
      const top=controlsBottom+35,bottom=Math.max(top+280,legendTop-20);
      return {x:width*.5,y:(top+bottom)/2,halfW:width*.44,halfH:(bottom-top)/2,focal:Math.max(350,width*.95)};
    }
    return {x:width*.66,y:height*.5,halfW:Math.max(170,width*.29),halfH:height*.43,focal:Math.min(height*.95,(width-300)*.75)};
  }
  function resize(){
    const rect=canvas.getBoundingClientRect();width=rect.width;height=rect.height;dpr=Math.min(devicePixelRatio||1,2);
    canvas.width=Math.max(1,Math.floor(width*dpr));canvas.height=Math.max(1,Math.floor(height*dpr));if(ctx)ctx.setTransform(dpr,0,0,dpr,0,0);
    const controls=document.querySelector(".explore-controls");$("app").style.setProperty("--controls-bottom",controls.offsetTop+controls.offsetHeight+18+"px");
    scheduleFrame();
  }
  function cameraSnapshot(){return {quaternion:state.camera.q.map(n=>Number(n.toFixed(6))),distance:Number(state.camera.distance.toFixed(3)),target:state.camera.target.map(n=>Number(n.toFixed(3))),pan:state.camera.pan.map(n=>Number(n.toFixed(3))),focused:state.camera.focused};}
  function updateCameraUI(){
    const zoom=Math.round(state.camera.baseDistance/state.camera.distance*100);$("zoom-level").textContent=zoom+"%";canvas.dataset.zoom=String(zoom);canvas.dataset.camera=JSON.stringify(cameraSnapshot());
  }
  function rotate(dx,dy,roll=0){
    const delta=qMultiply(qMultiply(qAxis([0,0,1],roll),qAxis([0,1,0],dx)),qAxis([1,0,0],dy));
    state.camera.q=qNormalize(qMultiply(delta,state.camera.q));scheduleFrame();
  }
  function fitGraph(speak=true){
    const pts=state.rendered;if(!pts.length){state.camera.target=[0,0,0];state.camera.distance=1400;}
    else{
      const bounds=[["x",0],["y",1],["z",2]].map(([key])=>[Math.min(...pts.map(p=>p[key])),Math.max(...pts.map(p=>p[key]))]);
      state.camera.target=bounds.map(([min,max])=>(min+max)/2);
      const v=viewport();state.camera.distance=fittedDistance(pts,state.camera.q,state.camera.target,v.focal,v.halfW,v.halfH);
    }
    state.camera.baseDistance=state.camera.distance;state.camera.pan=[0,0];state.camera.focused=null;updateCameraUI();scheduleFrame();if(speak)announce(t("fitted"));
  }
  function focusTopic(){
    if(!state.selected)return;
    state.camera.target=[state.selected.x,state.selected.y,state.selected.z];state.camera.pan=[0,0];state.camera.distance=180;state.camera.focused=state.selected.id;
    state.paused=true;updateRotate();setView("graph");$("detail").hidden=true;updateCameraUI();scheduleFrame();canvas.focus({preventScroll:true});announce(t("focused"));
  }
  function setZoom(factor,focusIfSelected=false){
    if(focusIfSelected&&state.selected&&state.camera.focused!==state.selected.id)focusTopic();
    state.camera.distance=zoomDistance(state.camera.distance,factor);updateCameraUI();scheduleFrame();
  }
  function resetCamera(){state.camera.q=initialQ();fitGraph();}
  function project(){
    const v=viewport(),c=state.camera;projected=[];
    for(const topic of state.rendered){
      const r=qRotate(c.q,[topic.x-c.target[0],topic.y-c.target[1],topic.z-c.target[2]]),den=c.distance-r[2];if(den<=8)continue;
      const scale=v.focal/den;
      projected[topic.index]={x:v.x+c.pan[0]+r[0]*scale,y:v.y+c.pan[1]+r[1]*scale,r:clamp(topic.radius*scale,1.2,topic.id===state.selected?.id?160:38),depth:r[2],scale,topic};
    }
    renderOrder=state.rendered.map(topic=>projected[topic.index]).filter(Boolean).sort((a,b)=>a.depth-b.depth);
  }
  function draw(time){
    raf=0;const elapsed=Math.min(50,time-(state.lastFrame||time));state.lastFrame=time;
    if(!state.paused&&!state.pointers.size&&!document.hidden&&state.view==="graph")state.camera.q=qNormalize(qMultiply(qAxis([0,1,0],elapsed*.000105),state.camera.q));
    ctx.fillStyle="#080e13";ctx.fillRect(0,0,width,height);project();
    const selected=state.selected,relevant=id=>selected&&(id===selected.id||state.lineage.has(id)||state.nextIds.has(id));
    for(const edge of state.edges){
      if(!state.visibleIds.has(edge.from)||!state.visibleIds.has(edge.to))continue;
      const a=projected[state.byId.get(edge.from).index],b=projected[state.byId.get(edge.to).index];if(!a||!b)continue;
      const highlight=selected&&relevant(edge.from)&&relevant(edge.to);
      ctx.setLineDash(edge.relation==="parte-da-habilidade"?[2,3]:[]);
      ctx.strokeStyle=highlight?"rgba(245,211,82,.66)":selected?"rgba(110,145,160,.018)":"rgba(134,166,181,.075)";ctx.lineWidth=highlight?1.2:.6;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke();
    }
    ctx.setLineDash([]);
    for(const p of renderOrder){
      if(p.x<-180||p.x>width+180||p.y<-180||p.y>height+180)continue;
      const isSelected=selected?.id===p.topic.id,isHover=state.hover?.id===p.topic.id;
      ctx.globalAlpha=selected&&!relevant(p.topic.id) ? .12 : clamp(p.scale+.25,.5,1);
      if(isSelected||isHover){ctx.globalAlpha=1;ctx.beginPath();ctx.arc(p.x,p.y,p.r+6,0,Math.PI*2);ctx.fillStyle="#f5d35218";ctx.fill();ctx.strokeStyle="#f5d35288";ctx.lineWidth=1;ctx.stroke();}
      ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle=isSelected?"#fff2a6":p.topic.color;ctx.fill();
    }
    ctx.globalAlpha=1;
    if(selected&&state.camera.focused===selected.id){
      const p=projected[selected.index];if(p){ctx.fillStyle="#f4f5ef";ctx.font="13px Arial";ctx.textAlign="center";const name=topicText(selected,"name");ctx.fillText(name.length>70?name.slice(0,67)+"...":name,p.x,Math.max(20,p.y-p.r-18));}
    }
    updateCameraUI();if(!state.paused&&!document.hidden&&state.view==="graph")raf=requestAnimationFrame(draw);
  }
  function scheduleFrame(){if(!raf&&ctx)raf=requestAnimationFrame(draw);}
  function pick(x,y){
    let found=null,best=Infinity;
    for(const p of renderOrder){const dist=Math.hypot(x-p.x,y-p.y);if(dist<Math.max(9,p.r+4)&&dist<best){found=p.topic;best=dist;}}
    return found;
  }
  function updateRotate(){$("rotate").textContent=state.paused?"▷":"Ⅱ";$("rotate").setAttribute("aria-pressed",String(state.paused));$("rotate").setAttribute("aria-label",t(state.paused?"play":"pause"));$("rotate").title=t(state.paused?"play":"pause");}
  function pointerPosition(event){const r=canvas.getBoundingClientRect();return {x:event.clientX-r.left,y:event.clientY-r.top};}
  function gestureSnapshot(){
    const points=[...state.pointers.values()];
    if(points.length<2)return null;const [a,b]=points;
    return {x:(a.x+b.x)/2,y:(a.y+b.y)/2,distance:Math.hypot(a.x-b.x,a.y-b.y),angle:Math.atan2(b.y-a.y,b.x-a.x)};
  }
  canvas.addEventListener("contextmenu",e=>e.preventDefault());
  canvas.addEventListener("pointerdown",e=>{
    if(![0,1,2].includes(e.button))return;e.preventDefault();canvas.focus({preventScroll:true});
    const p=pointerPosition(e);state.pointers.set(e.pointerId,{...p,startX:p.x,startY:p.y,moved:false,pan:e.button!==0||e.shiftKey,roll:e.altKey});
    canvas.setPointerCapture(e.pointerId);canvas.style.cursor="grabbing";$("tooltip").hidden=true;state.gesture=gestureSnapshot();
    if(state.pointers.size>1)for(const point of state.pointers.values())point.moved=true;
  });
  canvas.addEventListener("pointermove",e=>{
    const p=pointerPosition(e),previous=state.pointers.get(e.pointerId);
    if(previous){
      const dx=p.x-previous.x,dy=p.y-previous.y;previous.x=p.x;previous.y=p.y;previous.moved=previous.moved||Math.hypot(p.x-previous.startX,p.y-previous.startY)>4;
      if(state.pointers.size>=2){
        const next=gestureSnapshot(),old=state.gesture;
        if(old&&next){state.camera.pan[0]+=next.x-old.x;state.camera.pan[1]+=next.y-old.y;if(next.distance>5&&old.distance>5)state.camera.distance=zoomDistance(state.camera.distance,old.distance/next.distance);let roll=next.angle-old.angle;if(roll>Math.PI)roll-=Math.PI*2;if(roll<-Math.PI)roll+=Math.PI*2;rotate(0,0,roll);}
        state.gesture=next;
      }else if(previous.pan||e.shiftKey){state.camera.pan[0]+=dx;state.camera.pan[1]+=dy;}
      else if(previous.roll||e.altKey)rotate(0,0,dx*.006);
      else rotate(dx*.006,dy*.006);
      updateCameraUI();scheduleFrame();return;
    }
    state.hover=pick(p.x,p.y);canvas.style.cursor=state.hover?"pointer":"grab";
    if(state.hover){$("tooltip").innerHTML=esc(topicText(state.hover,"name"))+"<small>"+esc(subjectName(state.hover.subject))+"</small>";$("tooltip").hidden=false;$("tooltip").style.left=clamp(p.x+14,10,width-270)+"px";$("tooltip").style.top=clamp(p.y+14,10,height-90)+"px";}else $("tooltip").hidden=true;
    scheduleFrame();
  });
  function pointerEnd(e){
    const point=state.pointers.get(e.pointerId),wasSingle=state.pointers.size===1;state.pointers.delete(e.pointerId);state.gesture=gestureSnapshot();
    if(point&&wasSingle&&!point.moved&&!point.pan&&e.type==="pointerup"){const p=pointerPosition(e),topic=pick(p.x,p.y);if(topic)selectTopic(topic.id);}
    canvas.style.cursor=state.pointers.size?"grabbing":"grab";scheduleFrame();
  }
  canvas.addEventListener("pointerup",pointerEnd);canvas.addEventListener("pointercancel",pointerEnd);canvas.addEventListener("lostpointercapture",e=>{state.pointers.delete(e.pointerId);state.gesture=gestureSnapshot();});
  canvas.addEventListener("pointerleave",()=>{if(!state.pointers.size){state.hover=null;$("tooltip").hidden=true;scheduleFrame();}});
  canvas.addEventListener("wheel",e=>{e.preventDefault();const unit=e.deltaMode===1?16:e.deltaMode===2?height:1;setZoom(Math.exp(clamp(e.deltaY*unit,-500,500)*.0015));},{passive:false});
  canvas.addEventListener("keydown",e=>{
    const keys=["ArrowLeft","ArrowRight","ArrowUp","ArrowDown","+","=","-","_","Home","q","Q","e","E"];
    if(!keys.includes(e.key))return;e.preventDefault();
    if(e.key==="Home"){fitGraph();return;}
    if(["+","="].includes(e.key)){setZoom(.8);return;}if(["-","_"].includes(e.key)){setZoom(1.25);return;}
    if(["q","Q","e","E"].includes(e.key)){rotate(0,0,e.key.toLowerCase()==="q"?-.1:.1);return;}
    const dx=e.key==="ArrowLeft"?-.12:e.key==="ArrowRight"?.12:0,dy=e.key==="ArrowUp"?-.12:e.key==="ArrowDown"?.12:0;
    if(e.shiftKey){state.camera.pan[0]+=dx*200;state.camera.pan[1]+=dy*200;}else rotate(dx,dy);updateCameraUI();scheduleFrame();
  });
  $("zoom-in").addEventListener("click",()=>setZoom(.8,true));$("zoom-out").addEventListener("click",()=>setZoom(1.25));
  $("roll-left").addEventListener("click",()=>rotate(0,0,-.16));$("roll-right").addEventListener("click",()=>rotate(0,0,.16));
  $("focus-topic").addEventListener("click",focusTopic);$("detail-focus").addEventListener("click",focusTopic);
  $("show-details").addEventListener("click",()=>{if(state.selected){renderDetail();$("detail").hidden=false;}});
  $("fit-all").addEventListener("click",()=>fitGraph());$("reset-camera").addEventListener("click",resetCamera);
  $("rotate").addEventListener("click",()=>{state.paused=!state.paused;updateRotate();scheduleFrame();});
  $("subjects").addEventListener("click",e=>{const button=e.target.closest("[data-subject]");if(!button)return;const id=button.dataset.subject;state.active.has(id)?state.active.delete(id):state.active.add(id);button.setAttribute("aria-pressed",String(state.active.has(id)));applyFilters(true);});
  $("subjects-reset").addEventListener("click",()=>{state.active=new Set(state.subjects);buildSubjects();applyFilters(true);});
  $("subjects-none").addEventListener("click",()=>{clearSelection(false);state.active.clear();buildSubjects();applyFilters();announce(t("subjectsCleared"));});
  $("clear-filters").addEventListener("click",clearFilters);$("empty-reset").addEventListener("click",clearFilters);
  $("search").addEventListener("input",e=>{state.query=normalize(e.target.value.trim());applyFilters();});
  $("search").addEventListener("keydown",e=>{if(e.key==="ArrowDown"){const first=$("search-results").querySelector("button");if(first){e.preventDefault();first.focus();}}if(e.key==="Enter"&&state.filtered.length)selectTopic(state.filtered[0].id);});
  $("school-system").addEventListener("change",e=>{state.system=e.target.value;state.grade="all";updateGradeOptions();applyFilters(true);});
  $("grade").addEventListener("change",e=>{state.grade=e.target.value;applyFilters(true);});
  $("origin").addEventListener("change",e=>{state.origin=e.target.value;applyFilters(true);});
  $("language").addEventListener("change",e=>{state.lang=e.target.value;applyLanguage();try{const u=new URL(location.href);u.searchParams.set("lang",state.lang);history.replaceState(null,"",u.href);}catch{}});
  $("list-view").addEventListener("click",()=>setView("list"));$("graph-view").addEventListener("click",()=>setView("graph"));
  $("load-more").addEventListener("click",()=>{state.listLimit+=60;renderList();});
  [$("search-results"),$("results"),$("detail-content")].forEach(el=>el.addEventListener("click",e=>{const button=e.target.closest("[data-topic]");if(button)selectTopic(button.dataset.topic);if(e.target.closest("#translate-native"))translateConcept();}));
  document.querySelector(".skip-link").addEventListener("click",e=>{e.preventDefault();setView("list");});
  document.querySelector(".wordmark").addEventListener("click",e=>{e.preventDefault();clearFilters();setView("graph");resetCamera();});
  $("detail-close").addEventListener("click",()=>{clearSelection();$("search").focus({preventScroll:true});});
  $("detail-back").addEventListener("click",()=>{if(state.history.length)selectTopic(state.history.pop(),false);else clearSelection();});
  ["about-open","license-open"].forEach(id=>$(id).addEventListener("click",()=>$("about").showModal()));
  $("about-close").addEventListener("click",()=>$("about").close());
  $("about").addEventListener("click",e=>{if(e.target===$("about")){const r=$("about").getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$("about").close();}});
  document.addEventListener("click",e=>{if(!e.target.closest(".explore-controls"))$("search-results").hidden=true;});
  document.addEventListener("keydown",e=>{if(e.key==="Escape"&&!$("about").open){if(!$("detail").hidden)clearSelection();else $("search-results").hidden=true;}if(e.key==="/"&&!/INPUT|TEXTAREA|SELECT/.test(e.target.tagName)){e.preventDefault();$("search").focus();}});
  document.addEventListener("visibilitychange",()=>{state.lastFrame=0;if(!document.hidden)scheduleFrame();});
  window.addEventListener("resize",()=>{resize();if(state.loaded)fitGraph(false);});
  window.addEventListener("hashchange",()=>{const id=decodeURIComponent(location.hash.slice(1));if(state.byId.has(id))selectTopic(id);});
  async function translatorFor(source,target,status){
    source=languageCode(source);target=languageCode(target);if(source===target)return {translate:async text=>text};
    if(!("Translator" in root))throw new Error("unavailable");
    const key=source+"|"+target;
    if(!state.translators.has(key)){
      state.translators.set(key,(async()=>{
        const pair={sourceLanguage:source,targetLanguage:target};
        if(await root.Translator.availability(pair)==="unavailable")throw new Error("unavailable");
        return root.Translator.create({...pair,monitor:m=>m.addEventListener("downloadprogress",e=>{if(status.isConnected)status.textContent=t("translationDownload",{n:Math.round((e.loaded||0)*100)});})});
      })().catch(error=>{state.translators.delete(key);throw error;}));
    }
    return state.translators.get(key);
  }
  async function translateConcept(){
    const topic=state.selected,lang=state.lang;if(!topic)return;
    const status=$("translate-status"),button=$("translate-native");if(!status||!button)return;
    button.disabled=true;status.textContent=t("translationWorking");
    try{
      const jobs=[],main={_automatic:true};
      for(const field of ["name","description","domain"])if(topic[field])jobs.push({source:topic.language||"en",text:topic[field],save:value=>main[field]=value});
      const incoming=topic.prerequisites.filter(p=>state.byId.has(p.id)).slice(0,10),outgoing=(state.next.get(topic.id)||[]).slice(0,10);
      for(const related of [...incoming.map(p=>({topic:state.byId.get(p.id),reason:p.reason})),...outgoing]){
        if(jobs.length>=30)break;
        if(!hasTranslation(related.topic,"name"))jobs.push({source:related.topic.language||"en",text:related.topic.name,save:value=>state.autoTranslations.set(lang+"|"+related.topic.id,{...(state.autoTranslations.get(lang+"|"+related.topic.id)||{}),name:value,_automatic:true})});
        if(related.reason&&jobs.length<30)jobs.push({source:topic.language||"en",text:related.reason,save:value=>state.autoReasons.set(lang+"|"+topic.id+"|"+related.topic.id,value)});
      }
      let cursor=0;const run=async()=>{while(cursor<jobs.length){const job=jobs[cursor++],tr=await translatorFor(job.source,lang,status),text=await tr.translate(job.text);job.save(text);}};
      await Promise.all([run(),run()]);state.autoTranslations.set(lang+"|"+topic.id,main);
      if(state.lang===lang){if(state.selected?.id===topic.id)renderDetail();updateSearch();if(state.view==="list")renderList();}
    }catch(error){console.info("Local translation unavailable:",error);if(status.isConnected)status.textContent=t("translationUnavailable");if(button.isConnected)button.disabled=false;}
  }
  function cleanExportTopic(topic){const {searchText,color,index,x,y,z,radius,...data}=topic;return {...data,localized:{language:state.lang,name:topicText(topic,"name"),description:topicText(topic,"description"),domain:topicText(topic,"domain")}};}
  function download(content,type,name){const blob=new Blob([content],{type}),url=URL.createObjectURL(blob),link=document.createElement("a");link.href=url;link.download=name;document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);announce(t("exportPrepared",{n:number(state.filtered.length)}));}
  $("export-json").addEventListener("click",()=>download(JSON.stringify({metadata:{lang:state.lang,author:"Rodrigo Yú Matsumoto OAB/PE nº 1.338-B",keywords:"Rodrigo Yú Matsumoto OAB/PE nº 1.338-B",manager:"Rodrigo Yú Matsumoto OAB/PE nº 1.338-B",title:t("listTitle"),subject:t("listEyebrow"),databaseLicense:"ODbL-1.0",contentLicense:"CC-BY-SA-4.0",attribution:"Marble Skill Taxonomy (v1) · Generative Spark, Inc. (Marble) · https://withmarble.com",filters:{search:$("search").value,system:state.system,grade:state.grade,origin:state.origin,subjects:[...state.active]},relationNote:"relation:parte-da-habilidade represents composition, not a prerequisite.",exportedAt:new Date().toISOString()},topics:state.filtered.map(cleanExportTopic)},null,2),"application/json;charset=utf-8","Saber_Brasil_Conceitos.json"));
  $("export-csv").addEventListener("click",()=>{
    const cell=value=>{let text=String(value??"");if(/^\s*[=+@-]/.test(text))text="'"+text;return '"'+text.replaceAll('"','""')+'"';};
    const rows=[["id","name","description","subject","school_placements","origin","codes","connections","connection_types","database_license","content_license","attribution","language"]];
    state.filtered.forEach(topic=>rows.push([topic.id,topicText(topic,"name"),topicText(topic,"description"),subjectName(topic.subject),placements(topic).map(formatPlacement).join(" | "),topicOrigin(topic),topic.standards.map(s=>s.sourceCodeLiteral||s.code||s.sourceSection||"").join(" | "),topic.prerequisites.map(p=>p.id).join(" | "),topic.prerequisites.map(p=>p.relation||"pre-requisito").join(" | "),"ODbL-1.0","CC-BY-SA-4.0","Marble Skill Taxonomy (v1) · Generative Spark, Inc. (Marble) · https://withmarble.com",state.lang]));
    download("\ufeff"+rows.map(row=>row.map(cell).join(";")).join("\r\n"),"text/csv;charset=utf-8","Saber_Brasil_Conceitos.csv");
  });
  loadData();
})(typeof window==="object"?window:globalThis);
