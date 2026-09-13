const state = { stats: null, reports: [], alerts: [], actions: [], sites: [], activities: [], rules: [], user: JSON.parse(localStorage.getItem('sif_user') || 'null') };
const $ = (id) => document.getElementById(id);
const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (character) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' }[character]));
const formatDate = (value) => value ? new Date(value).toLocaleDateString('en-IN', { day: '2-digit', month: 'short' }) : '—';

async function api(path, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  const token = localStorage.getItem('sif_token');
  if (token) headers.Authorization = `Bearer ${token}`;
  const response = await fetch(path, { ...options, headers });
  if (response.status === 401) {
    localStorage.removeItem('sif_token');
    localStorage.removeItem('sif_user');
    window.location.reload();
    throw new Error('Session expired. Please sign in again.');
  }
  if (!response.ok) {
    let message = 'Request failed';
    try { message = (await response.json()).detail || message; } catch {}
    throw new Error(message);
  }
  return response.json();
}

function showLoading(isLoading) { $('loading').classList.toggle('show', isLoading); }
function rankMarkup(items, limit = 5) {
  const maximum = Math.max(...items.map((item) => item.density), 1);
  return items.slice(0, limit).map((item, index) => `<div class="ranking-item"><span class="rank">0${index + 1}</span><div><strong>${esc(item.name)}</strong><div class="bar-track"><div class="bar-fill" style="width:${Math.max(5, item.density / maximum * 100)}%"></div></div></div><span class="rank-value">${item.density}%</span></div>`).join('') || '<div class="empty-state">No data yet</div>';
}

async function loadData() {
  showLoading(true);
  try {
    [state.stats, state.reports, state.alerts, state.actions, state.sites, state.activities, state.rules] = await Promise.all([
      api('/dashboard/stats'), api('/reports/?limit=100'), api('/alerts/'), api('/actions/'),
      api('/dashboard/top-sites'), api('/dashboard/top-activities'), api('/dashboard/top-rules')
    ]);
    renderAll();
  } catch (error) {
    $('loading').textContent = error.message;
    $('loading').classList.add('show');
  } finally { setTimeout(() => showLoading(false), 600); }
}

function renderAll() {
  const stats = state.stats || {};
  $('total-reports').textContent = stats.total_reports ?? 0;
  $('sif-reports').textContent = stats.sif_reports ?? 0;
  $('non-sif-reports').textContent = stats.non_sif_reports ?? 0;
  $('high-alerts').textContent = stats.high_risk_alerts ?? 0;
  $('sif-rate').textContent = `${stats.sif_percentage ?? 0}% of all reports`;
  $('alert-count').textContent = stats.high_risk_alerts ?? 0;
  $('site-ranking').innerHTML = rankMarkup(state.sites);
  $('precursor-sites').innerHTML = rankMarkup(state.sites, 10);
  $('activity-ranking').innerHTML = rankMarkup(state.activities);
  $('precursor-list').innerHTML = state.rules.slice(0, 4).map((rule) => `<div class="precursor"><strong>${esc(rule.name)}</strong>${rule.sif_reports} SIF signals across ${rule.reports} reports (${rule.density}%)</div>`).join('') || '<div class="empty-state">No patterns yet</div>';
  renderReports(); renderAlerts(); renderActions(); drawCharts();
}

function renderReports() {
  const query = ($('report-search').value || '').toLowerCase();
  const risk = $('risk-filter').value;
  const reports = state.reports.filter((report) => (!risk || report.risk_level === risk) && (!query || `${report.report_text} ${report.location} ${report.activity}`.toLowerCase().includes(query)));
  $('reports-table').innerHTML = reports.map((report) => `<tr><td><strong>${esc(report.report_text)}</strong><span class="muted">${esc(report.report_type)} · ${formatDate(report.created_at)}</span></td><td>${esc(report.location)}</td><td>${esc(report.life_saving_rule)}</td><td><span class="badge ${report.risk_level.toLowerCase()}">${report.risk_level} · ${Math.round(report.sif_probability * 100)}%</span></td><td>${esc(report.status)}</td></tr>`).join('') || '<tr><td colspan="5" class="empty-state">No reports match this filter.</td></tr>';
}
function renderAlerts() { $('alerts-grid').innerHTML = state.alerts.map((alert) => `<article class="alert-card"><span class="badge high">${esc(alert.severity)} PRIORITY</span><h3>${esc(alert.report.activity)} · ${esc(alert.report.location)}</h3><p>${esc(alert.report.report_text)}</p><div class="alert-meta"><span>${esc(alert.report.life_saving_rule)}</span><span>${formatDate(alert.created_at)}</span><span>${esc(alert.status)}</span></div></article>`).join('') || '<div class="panel empty-state">No high-risk alerts.</div>'; }
function renderActions() { $('actions-table').innerHTML = state.actions.map((action) => `<tr><td><strong>${esc(action.description)}</strong></td><td>${esc(action.responsible)}</td><td><span class="badge ${action.priority.toLowerCase()}">${esc(action.priority)}</span></td><td>${formatDate(action.due_date)}</td><td>${esc(action.status)}</td></tr>`).join('') || '<tr><td colspan="5" class="empty-state">No corrective actions have been logged.</td></tr>'; }

let trendChart;
let rulesChart;
async function drawCharts() {
  try {
    const trend = await api('/dashboard/sif-trend');
    if (trendChart) trendChart.destroy();
    trendChart = new Chart($('trend-chart'), { type: 'line', data: { labels: trend.map((row) => row.date), datasets: [{ label: 'SIF potential', data: trend.map((row) => row.sif_reports), borderColor: '#16785d', backgroundColor: 'rgba(22,120,93,.1)', fill: true, tension: .35 }, { label: 'All reports', data: trend.map((row) => row.reports), borderColor: '#b7c7c0', borderDash: [4, 4], tension: .35 }] }, options: { responsive: true, plugins: { legend: { position: 'bottom' } }, scales: { y: { beginAtZero: true }, x: { grid: { display: false } } } } });
    if (rulesChart) rulesChart.destroy();
    rulesChart = new Chart($('rules-chart'), { type: 'doughnut', data: { labels: state.rules.slice(0, 6).map((row) => row.name), datasets: [{ data: state.rules.slice(0, 6).map((row) => row.sif_reports), backgroundColor: ['#16785d', '#e39b2f', '#d65b4b', '#3b7b89', '#8a9b53', '#bd7861'], borderWidth: 0 }] }, options: { cutout: '68%', plugins: { legend: { position: 'bottom' } } } });
  } catch (error) { console.error(error); }
}

function navigate(view) {
  document.querySelectorAll('.view').forEach((element) => element.classList.remove('active-view'));
  $(`view-${view}`).classList.add('active-view');
  document.querySelectorAll('.nav-item').forEach((element) => element.classList.toggle('active', element.dataset.view === view));
  $('page-title').textContent = { overview: 'Executive overview', analyzer: 'AI report analyzer', reports: 'Safety reports', alerts: 'SIF alerts', precursors: 'Precursor analysis', actions: 'Corrective actions' }[view];
}
function enterApp(user, token) { localStorage.setItem('sif_token', token); localStorage.setItem('sif_user', JSON.stringify(user)); state.user = user; $('auth-screen').classList.add('hidden'); $('app').classList.remove('hidden'); $('user-name').textContent = user.name; $('user-role').textContent = user.role; $('user-avatar').textContent = user.name.split(' ').map((part) => part[0]).join('').slice(0, 2).toUpperCase(); loadData(); }
function leaveApp() { localStorage.removeItem('sif_token'); localStorage.removeItem('sif_user'); window.location.reload(); }

document.querySelectorAll('[data-auth]').forEach((tab) => tab.addEventListener('click', () => { document.querySelectorAll('.auth-tab').forEach((button) => button.classList.toggle('active', button === tab)); $('login-pane').classList.toggle('hidden', tab.dataset.auth !== 'login'); $('register-pane').classList.toggle('hidden', tab.dataset.auth !== 'register'); }));
document.querySelectorAll('[data-demo]').forEach((button) => button.addEventListener('click', () => { const [username, password] = button.dataset.demo.split('|'); $('login-username').value = username; $('login-password').value = password; $('login-form').requestSubmit(); }));
$('login-form').addEventListener('submit', async (event) => { event.preventDefault(); $('login-error').textContent = ''; try { const result = await api('/auth/login', { method: 'POST', body: JSON.stringify({ username: $('login-username').value, password: $('login-password').value }) }); enterApp(result.user, result.access_token); } catch (error) { $('login-error').textContent = error.message; } });
$('register-form').addEventListener('submit', async (event) => { event.preventDefault(); $('register-error').textContent = ''; try { const result = await api('/auth/register', { method: 'POST', body: JSON.stringify({ name: $('register-name').value, username: $('register-username').value, email: $('register-email').value, password: $('register-password').value, role: $('register-role').value }) }); enterApp(result.user, result.access_token); } catch (error) { $('register-error').textContent = error.message; } });
$('analysis-form').addEventListener('submit', async (event) => { event.preventDefault(); const button = event.target.querySelector('button'); $('analysis-error').textContent = ''; button.disabled = true; button.textContent = 'Analyzing…'; try { const result = await api('/analysis/', { method: 'POST', body: JSON.stringify({ report_text: $('report-text').value, report_type: $('report-type').value, location: $('location').value, department: $('department').value, activity: $('activity').value, persist: true }) }); $('analysis-result').classList.remove('empty'); $('analysis-result').innerHTML = `<span class="result-kicker">MODEL ASSESSMENT · ${esc(result.sif_label)}</span><div class="result-title ${result.risk_level.toLowerCase()}">${esc(result.risk_level)} RISK</div><div class="result-score">SIF confidence <strong>${Math.round(result.sif_probability * 100)}%</strong></div><div class="permit-banner"><strong>${result.risk_level === 'LOW' ? '✓ Work may proceed under local controls' : '⛔ Work held for HSE review'}</strong><span>${result.risk_level === 'HIGH' ? 'A hazard alert email was sent when SMTP is configured.' : 'Continue following the approved safe-work procedure.'}</span></div><div class="result-details"><div class="detail"><span>Life-Saving Rule</span><strong>${esc(result.life_saving_rule)}</strong></div><div class="detail"><span>Activity</span><strong>${esc(result.activity)}</strong></div><div class="detail"><span>Barrier failure</span><strong>${esc(result.barrier_failure)}</strong></div><div class="detail"><span>Potential consequence</span><strong>${esc(result.potential_consequence)}</strong></div></div><p>${esc(result.explanation)}</p>`; await loadData(); } catch (error) { $('analysis-error').textContent = error.message; } finally { button.disabled = false; button.textContent = '✦ Analyze and save report'; } });

document.querySelectorAll('[data-view]').forEach((button) => button.addEventListener('click', () => navigate(button.dataset.view)));
document.querySelectorAll('[data-go]').forEach((button) => button.addEventListener('click', () => navigate(button.dataset.go)));
$('report-search').addEventListener('input', renderReports); $('risk-filter').addEventListener('change', renderReports); $('logout').addEventListener('click', leaveApp);
if (state.user && localStorage.getItem('sif_token')) { $('auth-screen').classList.add('hidden'); $('app').classList.remove('hidden'); $('user-name').textContent = state.user.name; $('user-role').textContent = state.user.role; loadData(); }
