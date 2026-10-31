# Disposable Community Cloud gate-0 spike for EdBot Study AI.
#
# Purpose: prove that the proven inline components-v2 full-bleed shell renders
# and round-trips on Streamlit Community Cloud, WITHOUT a database, network,
# or secrets. This is the cheapest first evidence gate (Gate 0 in docs/To-Do.md
# section 3.1). If Cloud cannot render this inline v2 shell at all, the React
# packaging question (Gate 1) is moot and the shell track defers to plain
# Streamlit IA tabs. If it renders and the Next-card loop works, Gate 1 is
# worth pursuing.
#
# Safety boundaries (deliberate):
#   - Uses FIXTURE cards only. It does NOT import core.personal.composition,
#     does NOT open the local Personal Workspace SQLite DB, and does NOT read
#     any database file.
#   - Does NOT import app.py or ui/personal_workspace.py.
#   - Does NOT read .env or .streamlit/secrets.toml and does NOT call st.secrets.
#   - Does NOT contact Google Drive, Supabase, PostgreSQL, pgvector, Voyage,
#     Gemini, Groq, or any AI provider. No network calls at all.
#   - Is disposable: deleting spike_cloud_app.py undoes this experiment. It is
#     meant to live on a separate Cloud branch, not the main app branch.
#
# The shell mechanism (parent CSS, component CSS, JS, data= channel,
# on_next_change callback, console diagnostics) is copied verbatim from the
# locally proven spike_app.py so Gate 0 tests exactly the mechanism that
# already worked on localhost, minus the database read.

import time
import html
import streamlit as st


FIXTURES = [
    {'front': 'What is the first-line drug for stable angina?', 'back': 'Beta blocker (e.g. atenolol) plus GTN for acute relief.'},
    {'front': 'Which part of the nephron reabsorbs the bulk of filtered Na+?', 'back': 'Proximal convoluted tubule (~65%).'},
    {'front': 'Key rate-limiting enzyme of glycolysis?', 'back': 'Phosphofructokinase-1 (PFK-1).'},
    {'front': 'Mechanism of action of warfarin?', 'back': 'Vitamin K epoxide reductase inhibitor; lowers factors II, VII, IX, X.'},
    {'front': 'Classic triad of pulmonary embolism?', 'back': 'Dyspnoea, pleuritic chest pain, haemoptysis (often incomplete).'},
    {'front': 'First-line therapy for absence seizures?', 'back': 'Ethosuximide (valproate if generalized co-seizures).'},
]


st.set_page_config(page_title='EdBot cloud spike', layout='wide', initial_sidebar_state='collapsed')

st.html('''<style>
html, body {margin:0 !important; padding:0 !important; background:#0f0f14 !important;}
[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl'], [data-testid='stHeader'], footer, [data-testid='stFooter'], [data-testid='stDecoration'], [data-testid='stStatusWidget'], .stApp > footer {display:none !important;}
[data-testid='stAppViewContainer'], [data-testid='stMain'], section.main, .block-container {background:#0f0f14 !important; margin:0 !important; padding:0 !important; max-width:100% !important;}
[data-testid='stMainBlockContainer'] {padding-top:0 !important;}
iframe, .stComponentV2, [data-testid='stComponent'], [data-testid='stElementContainer'] {display:block !important; width:100% !important; height:100vh !important; height:100dvh !important; min-height:100vh !important; min-height:100dvh !important; border:0 !important; margin:0 !important; padding:0 !important; background:#0f0f14 !important;}
</style>''')


def _clean(value, limit=5000):
    text = ' '.join(str(value or '').split())
    if len(text) > limit:
        return text[:limit - 3] + '...'
    return text


def _fallback_card(message):
    return {
        'id': '',
        'front': 'Cloud spike ready',
        'back': message,
        'source': 'fallback',
        'deck_id': '',
    }


def _pick_card_cloud(index):
    started = time.perf_counter()
    card_data = FIXTURES[index % len(FIXTURES)]
    card = {
        'id': 'fixture-' + str(index),
        'front': card_data['front'],
        'back': card_data['back'],
        'source': 'fixture',
        'deck_id': '',
    }
    elapsed = round((time.perf_counter() - started) * 1000)
    return card, elapsed


st.session_state.setdefault('render_count', 0)
st.session_state.setdefault('latency_ms', None)
st.session_state.setdefault('card', _fallback_card('Press Next card to load a fixture card.'))


def on_next():
    st.session_state.render_count = int(st.session_state.render_count) + 1
    card, elapsed = _pick_card_cloud(int(st.session_state.render_count))
    st.session_state.card = card
    st.session_state.latency_ms = elapsed


card = st.session_state.card
render_count = int(st.session_state.render_count)
latency_ms = st.session_state.latency_ms

front_raw = _clean(card.get('front', ''))
back_raw = _clean(card.get('back', ''))
front_attr = html.escape(front_raw, quote=True)
back_attr = html.escape(back_raw, quote=True)
front_text = html.escape(front_raw, quote=False)
back_text = html.escape(back_raw, quote=False)
id_attr = html.escape(_clean(card.get('id', '')), quote=True)
source_raw = _clean(card.get('source', ''))
source_attr = html.escape(source_raw, quote=True)
source_text = html.escape(source_raw, quote=False)
deck_attr = html.escape(_clean(card.get('deck_id', '')), quote=True)
latency_text = '?' if latency_ms is None else str(latency_ms)

HTML = f'''<div class='app' data-front='{front_attr}' data-back='{back_attr}' data-id='{id_attr}' data-source='{source_attr}' data-deck='{deck_attr}' data-render='{render_count}' data-latency='{latency_text}'>
  <div class='center'>
    <div class='top'>EdBot cloud spike · render {render_count} · source {source_text} · server {latency_text} ms</div>
    <div class='card' id='card' tabindex='0'>
      <div class='meta'></div>
      <div class='front'>{front_text}</div>
      <div class='back'>{back_text}</div>
    </div>
    <button id='next' type='button'>Next card</button>
    <div class='stat'></div>
  </div>
</div>'''

CSS = '''
html, body {
  height: 100%;
  margin: 0;
  padding: 0;
  background: #0f0f14;
}

.app {
  height: 100%;
  box-sizing: border-box;
  overflow: auto;
  display: flex;
  flex-direction: column;
  background: #0f0f14;
  color: #eee;
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
}

.center {
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
  padding: 2rem 1rem 3rem;
  width: 100%;
  max-width: 760px;
  box-sizing: border-box;
}

.top {
  opacity: .75;
  font-size: .9rem;
}

.card {
  width: min(92vw, 680px);
  min-height: 280px;
  padding: 2rem;
  border-radius: 20px;
  background: #16161d;
  border: 1px solid #2a2a36;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  box-shadow: 0 18px 60px rgba(0, 0, 0, .35);
}

.meta {
  color: #9f8cff;
  font-size: .85rem;
  min-height: 1.2em;
}

.front,
.back {
  font-size: 1.35rem;
  line-height: 1.45;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.back {
  display: none;
  color: #d7ffd7;
}

.card.flipped .front {
  display: none;
}

.card.flipped .back {
  display: block;
}

button {
  padding: .8rem 1.6rem;
  border: 0;
  border-radius: 12px;
  background: #7c5cff;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
}

button:disabled {
  opacity: .6;
  cursor: wait;
}

.stat {
  opacity: .7;
  font-size: .85rem;
}
'''

JS = '''
export default function (component) {
  const { parentElement, setTriggerValue } = component;
  console.log('cloud spike js ran', Date.now(), component.data);
  const app = parentElement.querySelector('.app');
  if (!app) {
    return;
  }

  const card = app.querySelector('#card');
  const meta = app.querySelector('.meta');
  const front = app.querySelector('.front');
  const back = app.querySelector('.back');
  const btn = app.querySelector('#next');
  const stat = app.querySelector('.stat');
  const data = app.dataset;

  if (front) {
    front.textContent = data.front || '';
  }

  if (back) {
    back.textContent = data.back || '';
  }

  if (meta) {
    const id = data.id ? ' · id ' + data.id : '';
    const deck = data.deck ? ' · deck ' + data.deck : '';
    meta.textContent = 'source: ' + (data.source || 'none') + id + deck;
  }

  if (stat) {
    stat.textContent = 'render ' + (data.render || '0') + ' · server ' + (data.latency || '?') + ' ms · click card to flip';
  }

  if (card) {
    card.classList.remove('flipped');
    card.onclick = function () {
      card.classList.toggle('flipped');
    };
    card.onkeydown = function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        card.classList.toggle('flipped');
      }
    };
  }

  if (btn) {
    btn.onclick = function () {
      btn.disabled = true;
      btn.textContent = 'Loading...';
      console.log('cloud spike button clicked', Date.now());
      setTriggerValue('next', true);
    };
  }
}
'''

shell = st.components.v2.component('edbot_spike_cloud', html=HTML, css=CSS, js=JS)
shell(key='spike_cloud', data={'render_count': render_count, 'latency_ms': latency_ms, 'card': card}, on_next_change=on_next)
