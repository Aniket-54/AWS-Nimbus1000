/* ── HireAI app.js ── */

// ── LOGIN ──────────────────────────────────────────────
const loginForm = document.getElementById('loginForm');
if (loginForm) {
  loginForm.addEventListener('submit', e => {
    e.preventDefault();
    window.location.href = 'index.html';
  });
}

// ── Everything below runs only on index.html ──────────
if (document.getElementById('navbar')) {

  // ── State ──────────────────────────────────────────
  let candidates = [];       // parsed CSV rows
  let filtered   = [];       // search-filtered subset
  let selected   = null;     // currently selected candidate

  // ── Nav: active link on scroll ─────────────────────
  const sections  = Array.from(document.querySelectorAll('.section'));
  const navLinks  = Array.from(document.querySelectorAll('.nav-link'));
  const NAV_H     = 64;

  function setActive(id) {
    navLinks.forEach(l => {
      l.classList.toggle('active', l.dataset.section === id);
    });
  }

  window.addEventListener('scroll', () => {
    let current = sections[0].id;
    for (const sec of sections) {
      if (window.scrollY >= sec.offsetTop - NAV_H - 10) current = sec.id;
    }
    setActive(current);
  }, { passive: true });

  // ── CSV/PDF Upload ──────────────────────────────────
  const csvInput    = document.getElementById('csvInput');
  const uploadBox   = document.getElementById('uploadBox');
  const uploadTrigger = document.getElementById('uploadTrigger');
  const fileChosen  = document.getElementById('fileChosen');
  const fileNameEl  = document.getElementById('fileName');
  const clearFile   = document.getElementById('clearFile');

  uploadTrigger.addEventListener('click', () => csvInput.click());
  uploadBox.addEventListener('click', e => { if (e.target !== uploadTrigger) csvInput.click(); });

  uploadBox.addEventListener('dragover', e => { e.preventDefault(); uploadBox.style.borderColor = 'var(--accent)'; });
  uploadBox.addEventListener('dragleave', () => { uploadBox.style.borderColor = ''; });
  uploadBox.addEventListener('drop', e => {
    e.preventDefault(); uploadBox.style.borderColor = '';
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  });

  csvInput.addEventListener('change', () => {
    if (csvInput.files[0]) handleFile(csvInput.files[0]);
  });

  clearFile.addEventListener('click', () => {
    candidates = []; filtered = [];
    csvInput.value = '';
    fileChosen.style.display = 'none';
    uploadBox.style.display  = '';
    resetResults();
  });

  function handleFile(file) {
    fileNameEl.textContent = file.name;
    fileChosen.style.display = 'flex';
    uploadBox.style.display  = 'none';
    if (file.name.toLowerCase().endsWith('.pdf')) {
      parsePDF(file);
    } else {
      parseCSV(file);
    }
  }

  // ── CSV Parser ──────────────────────────────────────
  function parseCSV(file) {
    const reader = new FileReader();
    reader.onload = e => {
      const lines = e.target.result.split('\n').filter(l => l.trim());
      if (lines.length < 2) return;
      const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
      candidates = lines.slice(1).map((line, i) => {
        const vals = splitCSVLine(line);
        const obj  = {};
        headers.forEach((h, idx) => { obj[h] = (vals[idx] || '').replace(/^"|"$/g, '').trim(); });
        obj._id    = i + 1;
        obj._score = Math.floor(Math.random() * 41) + 60;
        obj._reason = generateReason(obj);
        return obj;
      });
      filtered = [...candidates];
    };
    reader.readAsText(file);
  }

  // ── PDF Parser (single resume → one candidate) ──────
  function parsePDF(file) {
    // Without a PDF library we extract the raw text via FileReader as binary
    // and surface it as a single candidate entry for demo purposes.
    const reader = new FileReader();
    reader.onload = e => {
      // Pull printable ASCII text from the binary blob as a rough extraction
      const raw = Array.from(new Uint8Array(e.target.result))
        .map(b => (b >= 32 && b < 127) ? String.fromCharCode(b) : ' ')
        .join('').replace(/\s+/g, ' ').trim();
      const obj = {
        source: file.name,
        content_preview: raw.slice(0, 300) + (raw.length > 300 ? '…' : ''),
        _id: 1,
        _score: Math.floor(Math.random() * 41) + 60,
      };
      obj._reason = generateReason(obj);
      candidates = [obj];
      filtered   = [obj];
    };
    reader.readAsArrayBuffer(file);
  }

  function splitCSVLine(line) {
    const result = []; let cur = ''; let inQ = false;
    for (const ch of line) {
      if (ch === '"') { inQ = !inQ; }
      else if (ch === ',' && !inQ) { result.push(cur); cur = ''; }
      else { cur += ch; }
    }
    result.push(cur);
    return result;
  }

  // ── AI Reason Generator (mock — replaced by Bedrock in prod) ──
  function generateReason(c) {
    const scoreKey  = c._score;
    const skillKey  = guessKey(c, ['skills','skill','key_skills','technologies']);
    const expKey    = guessKey(c, ['years_experience','experience','exp','years']);
    const roleKey   = guessKey(c, ['category','job_title','position','title','role','designation']);
    const skills    = skillKey ? (c[skillKey] || '') : '';
    const exp       = expKey   ? (c[expKey]   || '') : '';
    const role      = roleKey  ? (c[roleKey]  || '') : '';

    const strengths = [], weaknesses = [];

    if (skills.length > 40)  strengths.push('broad and relevant skill set');
    else if (skills.length)  weaknesses.push('limited skills listed');

    const expNum = parseFloat(exp);
    if (!isNaN(expNum)) {
      if (expNum >= 5)       strengths.push(`strong ${expNum} years of experience`);
      else if (expNum >= 2)  strengths.push(`solid ${expNum} years of experience`);
      else                   weaknesses.push(`only ${expNum} year(s) of experience`);
    }

    if (role) strengths.push(`role aligns with "${role}"`);

    if (scoreKey >= 85)      strengths.push('high overall profile consistency');
    else if (scoreKey < 70)  weaknesses.push('profile lacks depth in key areas');

    const sStr = strengths.length  ? `Strengths: ${strengths.join(', ')}.`   : '';
    const wStr = weaknesses.length ? `Areas of concern: ${weaknesses.join(', ')}.` : '';
    return [sStr, wStr].filter(Boolean).join(' ') || 'Insufficient data for detailed analysis.';
  }

  function guessKey(obj, candidates) {
    if (!obj) return null;
    const keys = Object.keys(obj).map(k => k.toLowerCase());
    for (const c of candidates) {
      const idx = keys.indexOf(c);
      if (idx !== -1) return Object.keys(obj)[idx];
    }
    return null;
  }

  // ── Analyse button ──────────────────────────────────
  document.getElementById('analyseBtn').addEventListener('click', () => {
    if (!candidates.length) {
      alert('Please upload a CSV file first.');
      return;
    }
    // Sort by score desc
    candidates.sort((a, b) => b._score - a._score);
    filtered = [...candidates];
    renderResults(filtered);
    // Smooth scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
  });

  // ── Render results table ────────────────────────────
  function renderResults(data) {
    const tbody   = document.getElementById('resultsBody');
    const idKey   = guessKey(data[0], ['id','candidate_id','applicant_id','resume_id']);
    const roleKey = guessKey(data[0], ['category','job_title','position','title','role','designation']);
    const expKey  = guessKey(data[0], ['years_experience','experience','exp','years']);
    const skillKey= guessKey(data[0], ['skills','skill','key_skills','technologies']);

    if (!data.length) { resetResults(); return; }

    tbody.innerHTML = data.map((c, i) => {
      const scoreClass = c._score >= 80 ? 'score-high' : c._score >= 65 ? 'score-medium' : 'score-low';
      const id    = idKey    ? c[idKey]    : `C-${c._id}`;
      const role  = roleKey  ? c[roleKey]  : '—';
      const exp   = expKey   ? c[expKey]   : '—';
      const skills= skillKey ? (c[skillKey] || '').split(/[,;|]/).slice(0,3).join(', ') : '—';
      return `<tr data-idx="${candidates.indexOf(c)}" class="${selected && selected._id === c._id ? 'selected' : ''}">
        <td>${i + 1}</td>
        <td>${id}</td>
        <td>${role}</td>
        <td>${exp}</td>
        <td>${skills}</td>
        <td><span class="score-badge ${scoreClass}">${c._score}%</span></td>
      </tr>`;
    }).join('');

    // Row click → candidate detail
    tbody.querySelectorAll('tr').forEach(row => {
      row.addEventListener('click', () => {
        const idx = parseInt(row.dataset.idx);
        selectCandidate(candidates[idx]);
        tbody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
        row.classList.add('selected');
        document.getElementById('candidate').scrollIntoView({ behavior: 'smooth' });
      });
    });
  }

  function resetResults() {
    document.getElementById('resultsBody').innerHTML =
      '<tr class="empty-row"><td colspan="6">No results yet — upload a CSV and run analysis above.</td></tr>';
  }

  // ── Candidate detail ────────────────────────────────
  function selectCandidate(c) {
    selected = c;
    const card = document.getElementById('candidateCard');
    const keys = Object.keys(c).filter(k => !k.startsWith('_'));
    const roleKey  = guessKey(c, ['category','job_title','position','title','role','designation']);
    const skillKey = guessKey(c, ['skills','skill','key_skills','technologies']);
    const skills   = skillKey ? (c[skillKey] || '').split(/[,;|]/).map(s => s.trim()).filter(Boolean) : [];
    const initials = (roleKey && c[roleKey] ? c[roleKey].charAt(0) : 'C').toUpperCase();
    const scoreClass = c._score >= 80 ? 'score-high' : c._score >= 65 ? 'score-medium' : 'score-low';

    const detailItems = keys
      .filter(k => k !== skillKey)
      .map(k => `<div class="detail-item"><label>${k.replace(/_/g,' ')}</label><span>${c[k] || '—'}</span></div>`)
      .join('');

    const skillTags = skills.map(s => `<span class="skill-tag">${s}</span>`).join('');

    const verdictIcon  = c._score >= 80 ? '&#9989;' : c._score >= 65 ? '&#9888;&#65039;' : '&#10060;';
    const verdictLabel = c._score >= 80 ? 'Strong Match' : c._score >= 65 ? 'Moderate Match' : 'Weak Match';

    card.innerHTML = `
      <div class="candidate-header">
        <div class="candidate-avatar">${initials}</div>
        <div class="candidate-meta">
          <h3>Candidate #${c._id}</h3>
          <p>${roleKey ? c[roleKey] : 'Applicant'} &nbsp;·&nbsp;
             <span class="score-badge ${scoreClass}">${c._score}% AI Score</span>
          </p>
        </div>
      </div>

      <div class="ai-verdict ${scoreClass.replace('score-','')}">
        <span class="verdict-icon">${verdictIcon}</span>
        <div>
          <strong>${verdictLabel}</strong>
          <p>${c._reason || 'No AI analysis available yet.'}</p>
        </div>
      </div>

      <div class="detail-grid">${detailItems}</div>
      ${skills.length ? `<div class="detail-item"><label>Skills</label><div class="skills-list">${skillTags}</div></div>` : ''}
    `;
  }

  // ── Candidate section inline search ────────────────
  const candidateSearch = document.getElementById('candidateSearch');
  const candSearchResults = document.getElementById('candSearchResults');

  candidateSearch.addEventListener('input', function () {
    const q = this.value.trim().toLowerCase();
    candSearchResults.innerHTML = '';
    if (!q || !candidates.length) { candSearchResults.style.display = 'none'; return; }

    const matches = candidates.filter(c =>
      Object.values(c).some(v => String(v).toLowerCase().includes(q))
    ).slice(0, 8);

    if (!matches.length) {
      candSearchResults.innerHTML = '<div class="cand-result-item muted">No candidates found</div>';
      candSearchResults.style.display = 'block';
      return;
    }

    const roleKey = guessKey(matches[0], ['category','job_title','position','title','role','designation']);
    matches.forEach(c => {
      const item = document.createElement('div');
      item.className = 'cand-result-item';
      const scoreClass = c._score >= 80 ? 'score-high' : c._score >= 65 ? 'score-medium' : 'score-low';
      item.innerHTML = `
        <span class="cri-id">Candidate #${c._id}</span>
        <span class="cri-role">${roleKey ? c[roleKey] : '—'}</span>
        <span class="score-badge ${scoreClass}">${c._score}%</span>
      `;
      item.addEventListener('click', () => {
        selectCandidate(c);
        candSearchResults.style.display = 'none';
        candidateSearch.value = '';
      });
      candSearchResults.appendChild(item);
    });
    candSearchResults.style.display = 'block';
  });

  document.addEventListener('click', e => {
    if (!e.target.closest('.cand-search-wrap')) candSearchResults.style.display = 'none';
  });

  // ── Nav search bar ──────────────────────────────────
  document.getElementById('searchBar').addEventListener('input', function () {
    const q = this.value.trim().toLowerCase();
    if (!candidates.length) return;
    if (!q) { filtered = [...candidates]; renderResults(filtered); return; }
    filtered = candidates.filter(c =>
      Object.values(c).some(v => String(v).toLowerCase().includes(q))
    );
    renderResults(filtered);
    if (!document.getElementById('results').getBoundingClientRect().top < window.innerHeight) {
      document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    }
  });

} // end index.html block
