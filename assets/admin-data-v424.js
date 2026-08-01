(() => {
  "use strict";
  if (window.__teAdminDataV424) return;
  window.__teAdminDataV424 = true;

  const OWNER = "chinoyuuki3-del";
  const REPO = "Troll-Engine-yuuki";
  const BRANCH = "main";
  const AUTH_KEY = "troll-engine-github-auth-v4.20";
  const SOURCES = [
    {id:"worlds", icon:"🌍", label:"公開ワールド", path:"data/public-worlds.json", hints:["worlds"]},
    {id:"videos", icon:"🎬", label:"AFT動画", path:"data/aft-videos.json", hints:["videos","items"]},
    {id:"users", icon:"👤", label:"ユーザー", path:"users.json", hints:["users","accounts","items"]},
    {id:"storage", icon:"💾", label:"保存データ", path:"data/storage.json", hints:["items","records","data"]},
    {id:"features", icon:"🎛️", label:"機能設定", path:"features.json", hints:["features","switches"]},
    {id:"safety", icon:"🛡️", label:"安全ルール", path:"safety-rules.json", hints:["rules","items"]},
    {id:"news", icon:"📰", label:"お知らせ", path:"news.json", hints:["news","items"]},
    {id:"status", icon:"🚦", label:"稼働状況", path:"status.json", hints:["services","items"]}
  ];
  const $ = id => document.getElementById(id);
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  let auth = null;
  let active = SOURCES[0];
  let rawData = null;
  let rows = [];
  let jsonMode = false;

  function readAuth(){
    try { return JSON.parse(sessionStorage.getItem(AUTH_KEY) || "null"); }
    catch { return null; }
  }
  function isAdmin(value){ return value?.token && String(value?.user?.login || "").toLowerCase() === OWNER.toLowerCase(); }
  function headers(){
    const h = {Accept:"application/vnd.github+json"};
    if (auth?.token) h.Authorization = `Bearer ${auth.token}`;
    return h;
  }
  function setStatus(message, type=""){
    const el=$("teAdmStatus"); if(!el)return; el.className=`admStatus ${type}`; el.textContent=message;
  }
  function openAccountLink(){
    const tab=$("te420GithubBackupTab");
    if(tab){ showTab("te420GithubBackupMain", tab); setTimeout(()=>document.querySelector('[data-te420-panel="account"]')?.click(),80); }
    else alert("GitHub保存センターを開いて、最高管理者アカウントを連携してください。");
  }
  function renderGate(){
    auth=readAuth();
    const gate=$("teAdmGate"), shell=$("teAdmShell");
    if(!gate||!shell)return false;
    if(isAdmin(auth)){
      gate.innerHTML=`✅ <b>@${esc(auth.user.login)}</b> を最高管理者として確認しました。下の管理メニューから内容を見られます。`;
      gate.style.borderColor="rgba(52,211,153,.35)"; gate.style.background="rgba(6,78,59,.18)";
      shell.classList.remove("admHidden"); return true;
    }
    shell.classList.add("admHidden");
    gate.innerHTML=`🔒 この画面は最高管理者専用です。<br><button id="teAdmLink" type="button" class="mainBtn" style="margin-top:9px">Troll Engine内でGitHub連携</button>`;
    $("teAdmLink")?.addEventListener("click",openAccountLink); return false;
  }
  function renderMenu(){
    const menu=$("teAdmMenu"); if(!menu)return;
    menu.innerHTML=SOURCES.map(s=>`<button type="button" data-adm-source="${s.id}" class="${s.id===active.id?"active":""}">${s.icon} ${esc(s.label)}<br><small>${esc(s.path)}</small></button>`).join("");
    menu.querySelectorAll("[data-adm-source]").forEach(btn=>btn.onclick=()=>selectSource(btn.dataset.admSource));
  }
  function decodeBase64(text){
    const bin=atob(String(text||"").replace(/\s/g,""));
    const bytes=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++)bytes[i]=bin.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  }
  async function fetchJson(source){
    const path=source.path.split("/").map(encodeURIComponent).join("/");
    const api=`https://api.github.com/repos/${OWNER}/${REPO}/contents/${path}?ref=${encodeURIComponent(BRANCH)}&t=${Date.now()}`;
    const res=await fetch(api,{cache:"no-store",headers:headers()});
    if(res.status===404) throw new Error(`${source.path} はまだ作成されていません。`);
    if(!res.ok) throw new Error(`GitHub API エラー ${res.status}`);
    const body=await res.json();
    if(body.encoding!=="base64"||typeof body.content!=="string")throw new Error("ファイル内容を読み取れませんでした。");
    return JSON.parse(decodeBase64(body.content));
  }
  function detectRows(data, source){
    if(Array.isArray(data)) return data;
    if(!data||typeof data!=="object") return [{value:data}];
    for(const key of source.hints){ if(Array.isArray(data[key])) return data[key]; }
    const firstArray=Object.values(data).find(Array.isArray); if(firstArray)return firstArray;
    return Object.entries(data).map(([key,value])=>({key,value}));
  }
  function scalar(value){ return value===null||["string","number","boolean"].includes(typeof value); }
  function short(value){
    if(scalar(value))return String(value??"");
    if(Array.isArray(value))return `[${value.length}件]`;
    if(typeof value==="object")return `{${Object.keys(value).length}項目}`;
    return String(value);
  }
  function columnNames(list){
    const score=new Map();
    for(const row of list.slice(0,100)){
      if(!row||typeof row!=="object"||Array.isArray(row))continue;
      for(const key of Object.keys(row))score.set(key,(score.get(key)||0)+1);
    }
    return [...score.entries()].sort((a,b)=>b[1]-a[1]).slice(0,8).map(x=>x[0]);
  }
  function matches(row, query){
    if(!query)return true;
    try{return JSON.stringify(row).toLowerCase().includes(query);}catch{return false;}
  }
  function renderStats(filtered){
    const box=$("teAdmStats"); if(!box)return;
    const bytes=new Blob([JSON.stringify(rawData??null)]).size;
    box.innerHTML=`<div class="admStat"><b>${rows.length}</b><small>全レコード</small></div><div class="admStat"><b>${filtered.length}</b><small>表示中</small></div><div class="admStat"><b>${Math.max(1,Math.round(bytes/1024))} KB</b><small>JSONサイズ</small></div><div class="admStat"><b>${esc(active.label)}</b><small>選択中</small></div>`;
  }
  function renderDetail(row,index){
    const box=$("teAdmDetail"); if(!box)return;
    box.classList.remove("admHidden");
    if(!row||typeof row!=="object")box.innerHTML=`<h3>詳細</h3><pre>${esc(String(row))}</pre>`;
    else box.innerHTML=`<h3>${esc(active.label)}：${index+1}件目の詳細</h3><div class="admDetailGrid">${Object.entries(row).map(([k,v])=>`<div class="key">${esc(k)}</div><div>${scalar(v)?esc(String(v??"")):`<pre>${esc(JSON.stringify(v,null,2))}</pre>`}</div>`).join("")}</div>`;
  }
  function renderView(){
    const view=$("teAdmView"), query=String($("teAdmSearch")?.value||"").trim().toLowerCase(); if(!view)return;
    const filtered=rows.map((row,index)=>({row,index})).filter(x=>matches(x.row,query)); renderStats(filtered);
    if(jsonMode){ view.innerHTML=`<pre>${esc(JSON.stringify(rawData,null,2))}</pre>`; return; }
    if(!filtered.length){ view.innerHTML='<div class="admEmpty">一致するデータがありません。</div>'; return; }
    const cols=columnNames(filtered.map(x=>x.row));
    if(!cols.length){view.innerHTML=`<pre>${esc(JSON.stringify(filtered.map(x=>x.row),null,2))}</pre>`;return;}
    view.innerHTML=`<div class="admTableWrap"><table><thead><tr><th>#</th>${cols.map(c=>`<th>${esc(c)}</th>`).join("")}<th>詳細</th></tr></thead><tbody>${filtered.slice(0,1000).map(({row,index})=>`<tr><td>${index+1}</td>${cols.map(c=>`<td>${scalar(row?.[c])?esc(short(row?.[c])):`<span class="admCellObject">${esc(short(row?.[c]))}</span>`}</td>`).join("")}<td><button type="button" class="grayBtn" data-adm-row="${index}">見る</button></td></tr>`).join("")}</tbody></table></div>`;
    view.querySelectorAll("[data-adm-row]").forEach(btn=>btn.onclick=()=>renderDetail(rows[Number(btn.dataset.admRow)],Number(btn.dataset.admRow)));
  }
  async function loadActive(){
    if(!renderGate())return;
    setStatus(`${active.label}をGitHubから読み込んでいます…`); $("teAdmDetail")?.classList.add("admHidden");
    try{
      rawData=await fetchJson(active); rows=detectRows(rawData,active); jsonMode=false; $("teAdmJson").textContent="JSON表示"; renderView();
      setStatus(`${active.label}を読み込みました。GitHubの生ファイルを開かず、この画面で確認できます。`,"good");
    }catch(error){ rawData=null; rows=[]; renderView(); setStatus(error?.message||String(error),"bad"); }
  }
  function selectSource(id){ active=SOURCES.find(s=>s.id===id)||SOURCES[0]; renderMenu(); loadActive(); }
  async function copyCurrent(){
    if(rawData==null)return setStatus("コピーするデータがありません。","bad");
    try{await navigator.clipboard.writeText(JSON.stringify(rawData,null,2));setStatus(`${active.label}の内容をコピーしました。`,"good");}
    catch{setStatus("クリップボードへコピーできませんでした。","bad");}
  }
  function boot(){
    renderMenu(); renderGate();
    $("teAdmReload")?.addEventListener("click",loadActive);
    $("teAdmSearch")?.addEventListener("input",renderView);
    $("teAdmJson")?.addEventListener("click",()=>{jsonMode=!jsonMode;$("teAdmJson").textContent=jsonMode?"表に戻す":"JSON表示";renderView();});
    $("teAdmCopy")?.addEventListener("click",copyCurrent);
    window.addEventListener("storage",renderGate);
    setInterval(()=>{const now=readAuth();if((now?.user?.login||"")!==(auth?.user?.login||""))renderGate();},2500);
  }
  window.teAdminDataV424={open:()=>{renderGate();if(isAdmin(readAuth())&&rawData==null)loadActive();},reload:loadActive};
  if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",boot,{once:true});else boot();
})();
