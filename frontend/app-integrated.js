/* ── HireAI app.js - Integrated with Backend API ── */

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
  let candidates = [];       // parsed CSV rows or API results
  let filtered   = [];       // search-filtered subset
  let selected   = null;     // currently selected candidate
  let uploadedPDFs = [];     // Track uploaded PDF files

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
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  });

  csvInput.addEventListener('change', () => {
    const files = Array.from(csvInput.files);
    handleFiles(files);
  });

  clearFile.addEventListener('click', () => {
    candidates = []; filtered = []; uploadedPDFs = [];
    csvInput.value = '';
    fileChosen.style.display = 'none';
    uploadBox.style.display  = '';
    resetResults();
  });

  function handleFiles(files) {
    if (!files.length) return;
    
    const pdfFiles = files.filter(f => f.name.toLowerCase().endsWith('.pdf'));
    const csvFiles = files.filter(f => f.name.toLowerCase().endsWith('.csv'));
    
    if (pdfFiles.length > 0) {
      fileNameEl.textContent = `${pdfFiles.length} PDF file(s) selected`;
      fileChosen.style.display = 'flex';
      uploadBox.style.display  = 'none';
      uploadedPDFs = pdfFiles;
    } else if (csvFiles.length > 0) {
      fileNameEl.textContent = csvFiles[0].name;
      fileChosen.style.display = 'flex';
      uploadBox.style.display  = 'none';
      parseCSV(csvFiles[0]);
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
    const scoreKey  = c._score || c.final_score;
    const skillKey  = guessKey(c, ['skills','skill','key_skills','technologies']);
    const expKey    = guessKey(c, ['years_experience','experience','exp','years','experience_years']);
    const roleKey   = guessKey(c, ['category','job_title','position','title','role','designation']);
    const skills    = skillKey ? (c[skillKey] || '') : '';
    const exp       = expKey   ? (c[expKey]   || '') : '';
    const role      = roleKey  ? (c[roleKey]  || '') : '';

    const strengths = [], weaknesses = [];

    if (typeof skills === 'string' && skills.length > 40)  strengths.push('broad and relevant skill set');
    else if (Array.isArray(skills) && skills.length > 5)   strengths.push('broad and relevant skill set');
    else if (skills)  weaknesses.push('limited skills listed');

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

  // ── Analyse button (with API integration) ──────────
  document.getElementById('analyseBtn').addEventListener('click', async () => {
    const promptInput = document.getElementById('promptInput').value.trim();
    
    if (!promptInput) {
      alert('Please enter a job description or search query.');
      return;
    }

    // Show loading state
    const analyseBtn = document.getElementById('analyseBtn');
    const originalText = analyseBtn.textContent;
    analyseBtn.textContent = '⏳ Processing...';
    analyseBtn.disabled = true;

    try {
      if (uploadedPDFs.length > 0) {
        // Upload PDFs first, then search
        await uploadPDFsToAPI(uploadedPDFs);
      }
      
      // Search candidates using the API
      await searchCandidates(promptInput);
      
      // Scroll to results
      document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
    } catch (error) {
      console.error('Error:', error);
      alert('Error processing request. Check console for details.');
    } finally {
      analyseBtn.textContent = originalText;
      analyseBtn.disabled = false;
    }
  });

  // ── Upload PDFs to API ──────────────────────────────
  async function uploadPDFsToAPI(files) {
    const endpoint = API_ENDPOINTS.uploadPDF();
    
    for (const file of files) {
      try {
        // Convert file to base64
        const base64 = await fileToBase64(file);
        
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            file: base64.split(',')[1], // Remove data:application/pdf;base64, prefix
            filename: file.name
          })
        });

        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('Upload successful:', result);
      } catch (error) {
        console.error(`Error uploading ${file.name}:`, error);
        throw error;
      }
    }
  }

  function fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  // ── Search Candidates via API ──────────────────────
  async function searchCandidates(query) {
    const endpoint = API_ENDPOINTS.search();
    
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
      });

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Transform API response to match frontend format
      candidates = data.results.map((c, i) => ({
        ...c,
        _id: c.candidate_id || i + 1,
        _score: Math.round((c.final_score || 0) * 100),
        _reason: c.reason || generateReason(c)
      }));
      
      filtered = [...candidates];
      renderResults(filtered);
    } catch (error) {
      console.error('Search error:', error);
      
      // Fallback to local CSV data if API fails
      if (candidates.length > 0) {
        alert('API unavailable. Using local CSV data.');
        candidates.sort((a, b) => b._score - a._score);
        filtered = [...candidates];
        renderResults(filtered);
      } else {
        throw error;
      }
    }
  }

  // ── Render results table ────────────────────────────
  function renderResults(data) {
    const tbody   = document.getElementById('resultsBody');
    const idKey   = guessKey(data[0], ['id','candidate_id','applicant_id','resume_id']);
    const roleKey = guessKey(data[0], ['category','job_title','position','title','role','designation']);
    const expKey  = guessKey(data[0], ['years_experience','experience','exp','years','experience_years']);
    const skillKey= guessKey(data[0], ['skills','skill','key_skills','technologies']);

    if (!data.length) { resetResults(); return; }

    tbody.innerHTML = data.map((c, i) => {
      const scoreClass = c._score >= 80 ? 'score-high' : c._score >= 65 ? 'score-medium' : 'score-low';
      const id    = idKey    ? c[idKey]    : `C-${c._id}`;
      const role  = roleKey  ? c[roleKey]  : '—';
      const exp   = expKey   ? c[expKey]   : '—';
      
      let skills = '—';
      if (skillKey) {
        const skillData = c[skillKey];
        if (Array.isArray(skillData)) {
          skills = skillData.slice(0, 3).join(', ');
        } else if (typeof skillData === 'string') {
          skills = skillData.split(/[,;|]/).slice(0, 3).join(', ');
        }
      }
      
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
      '<tr class="empty-row"><td colspan="6">No results yet — upload a CSV/PDF and run analysis above.</td></tr>';
  }

  // ── Candidate detail ────────────────────────────────
  function selectCandidate(c) {
    selected = c;
    const card = document.getElementById('candidateCard');
    const keys = Object.keys(c).filter(k => !k.startsWith('_'));
    const roleKey  = guessKey(c, ['category','job_title','position','title','role','designation']);
    const skillKey = guessKey(c, ['skills','skill','key_skills','technologies']);
    
    let skills = [];
    if (skillKey) {
      const skillData = c[skillKey];
      if (Array.isArray(skillData)) {
        skills = skillData;
      } else if (typeof skillData === 'string') {
        skills = skillData.split(/[,;|]/).map(s => s.trim()).filter(Boolean);
      }
    }
    
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
