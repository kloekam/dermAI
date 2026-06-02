const chatFab = document.getElementById('chatFab');
const openChatBtn = document.getElementById('openChatBtn');
const closeChatBtn = document.getElementById('closeChatBtn');
const chatPanel = document.getElementById('chatPanel');
const chatThread = document.getElementById('chatThread');
const chatForm = document.getElementById('chatForm');
const questionInput = document.getElementById('questionInput');
const skinTypeSelect = document.getElementById('skinTypeSelect');
const entityTypeSelect = document.getElementById('entityTypeSelect');
let history = [];

function setPanel(open){
  chatPanel.classList.toggle('open', open);
  chatPanel.setAttribute('aria-hidden', open ? 'false' : 'true');
  if(open) questionInput.focus();
}
chatFab.addEventListener('click', ()=>setPanel(true));
openChatBtn.addEventListener('click', ()=>setPanel(true));
closeChatBtn.addEventListener('click', ()=>setPanel(false));

document.querySelector('[data-theme-toggle]').addEventListener('click', ()=>{
  const root = document.documentElement;
  const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  root.setAttribute('data-theme', next);
});

function appendMessage(text, who='assistant', sources=[]){
  const wrap = document.createElement('div');
  wrap.className = `message ${who === 'user' ? 'user-message' : 'assistant-message'}`;
  wrap.textContent = text;
  if(sources.length){
    const holder = document.createElement('div');
    holder.className = 'sources';
    sources.forEach(s => {
      const chip = document.createElement('span');
      chip.className = 'source-chip';
      let label = `${s.name} · ${s.entity_type}`;
      if(s.page_number) label += ` · p.${s.page_number}`;
      holder.appendChild(chip);
      chip.textContent = label;
    });
    wrap.appendChild(holder);
  }
  chatThread.appendChild(wrap);
  chatThread.scrollTop = chatThread.scrollHeight;
}

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const question = questionInput.value.trim();
  if(!question) return;
  appendMessage(question, 'user');
  questionInput.value = '';
  const typing = document.createElement('div');
  typing.className = 'message assistant-message';
  typing.textContent = 'dermAI is searching the knowledge base...';
  chatThread.appendChild(typing);
  chatThread.scrollTop = chatThread.scrollHeight;
  try {
    const res = await fetch('/ask', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        question,
        filters: {
          skin_type: skinTypeSelect.value,
          entity_type: entityTypeSelect.value
        },
        history: history.slice(-5)
      })
    });
    const data = await res.json();
    typing.remove();
    appendMessage(data.answer || 'No answer returned.', 'assistant', data.sources || []);
    history.push({question, answer: data.answer || ''});
  } catch(err){
    typing.remove();
    appendMessage('Something went wrong while contacting dermAI.', 'assistant');
  }
});
