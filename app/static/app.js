const money = value => new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(value);
const modal = document.querySelector('#lead-modal');

async function api(url, options={}) {
  const response = await fetch(url,{headers:{'Content-Type':'application/json'},...options});
  if (!response.ok) throw new Error((await response.json()).detail || 'Request failed');
  return response.status === 204 ? null : response.json();
}

function openModal(){ modal.showModal(); }
function closeModal(){ modal.close(); }
function toast(message){ const node=document.createElement('div');node.className='toast';node.textContent=message;document.body.append(node);setTimeout(()=>node.remove(),4200); }

async function loadMetrics(){
  const data=await api('/api/metrics');
  const cards=[['Total leads',data.total_leads,'In your CRM'],['Hot opportunities',data.hot_leads,'Score of 70+'],['Pipeline value',money(data.pipeline_value),'Active opportunities'],['Meetings',data.meetings,'Currently booked']];
  document.querySelector('#metrics').innerHTML=cards.map(c=>`<div class="metric"><small>${c[0]}</small><strong>${c[1]}</strong><small>${c[2]}</small></div>`).join('');
  document.querySelector('#recommendation').textContent=data.hot_leads?`You have ${data.hot_leads} hot lead${data.hot_leads===1?'':'s'} ready for personal follow-up.`:'Add complete lead details to improve qualification scores.';
}

async function loadLeads(){
  const leads=await api('/api/leads');
  document.querySelector('#leads').innerHTML=leads.map(l=>`<tr><td><span class="company">${l.company}<small>${l.industry} · ${l.location||'No location'}</small></span></td><td><span class="score ${l.score>=70?'hot':l.score>=45?'warm':''}">${l.score}</span></td><td><select class="pill" onchange="changeStage(${l.id},this.value)">${['New','Qualified','Contacted','Replied','Meeting','Proposal','Won','Lost'].map(s=>`<option ${s===l.stage?'selected':''}>${s}</option>`).join('')}</select></td><td>${money(l.estimated_value)}</td><td><button class="draft" onclick='showDraft(${JSON.stringify(l.outreach_draft)})'>View draft</button></td></tr>`).join('');
}

async function loadTasks(){
  const tasks=await api('/api/tasks');
  document.querySelector('#tasks').innerHTML=tasks.map(t=>`<label class="task ${t.completed?'done':''}"><input type="checkbox" ${t.completed?'checked':''} onchange="toggleTask(${t.id})"><span>${t.title}<small>${t.due_date||'No due date'} · ${t.priority}</small></span></label>`).join('');
}

async function refresh(){ await Promise.all([loadMetrics(),loadLeads(),loadTasks()]); }
async function changeStage(id,stage){ await api(`/api/leads/${id}`,{method:'PATCH',body:JSON.stringify({stage})});await refresh(); }
async function toggleTask(id){ await api(`/api/tasks/${id}/toggle`,{method:'PATCH'});await loadTasks(); }
function showDraft(draft){ toast(draft); }

async function generateDemo(){
  const industry=prompt('Target industry','Cleaning Services'); if(!industry)return;
  const location=prompt('Target location','Austin, Texas'); if(!location)return;
  await api('/api/leads/generate',{method:'POST',body:JSON.stringify({industry,location,service:'website redesign and lead automation',count:3})});
  toast('3 fictional demo leads created. Verify real data before outreach.'); await refresh();
}

document.querySelector('#lead-form').addEventListener('submit',async event=>{
  event.preventDefault(); const form=new FormData(event.target); const data=Object.fromEntries(form.entries()); data.estimated_value=Number(data.estimated_value||0);
  try{ await api('/api/leads',{method:'POST',body:JSON.stringify(data)});event.target.reset();closeModal();toast('Lead scored and added.');await refresh(); }catch(error){toast(error.message)}
});

document.querySelector('#task-form').addEventListener('submit',async event=>{
  event.preventDefault(); const input=document.querySelector('#task-title'); await api('/api/tasks',{method:'POST',body:JSON.stringify({title:input.value})});input.value='';await loadTasks();
});

refresh().catch(error=>toast(error.message));

